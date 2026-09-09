# #!/usr/bin/env python3
# import json
# import queue
# import sys
# from pathlib import Path

# import sounddevice as sd
# from vosk import KaldiRecognizer, Model
# import pyttsx3

# MODEL_PATH = Path("vosk-model-ru-0.22")
# SAMPLE_RATE = 16_000
# BLOCK_SIZE = 8_000

# audio_queue = queue.Queue()


# def audio_callback(indata, frames, time_info, status):
#     """Получает необработанный звук из потока микрофона."""
#     if status:
#         print(f"Audio status: {status}", file=sys.stderr)

#     audio_queue.put(bytes(indata))


# def create_tts():
#     engine = pyttsx3.init()

#     # Скорость речи: eSpeak хорошо звучит примерно в диапазоне 130–170.
#     engine.setProperty("voice", "russian+f2")
#     engine.setProperty("rate", 109)
#     engine.setProperty("volume", 1.0)

#     return engine


# def speak(engine, text):
#     print(f"🔊 Повторяю: {text}")
#     engine.say(text)
#     engine.runAndWait()


# def main():
#     if not MODEL_PATH.is_dir():
#         print(
#             f"Не найдена модель Vosk: {MODEL_PATH.resolve()}\n"
#             "Скачай и распакуй русскую модель, затем проверь MODEL_PATH."
#         )
#         sys.exit(1)

#     print("Загружаю локальную модель Vosk…")


#     model = Model(str(MODEL_PATH))
#     recognizer = KaldiRecognizer(model, SAMPLE_RATE)
#     recognizer.SetWords(True)

#     tts = create_tts()

#     print("\nОфлайн-голосовой повторитель запущен.")
#     print("Говори в микрофон. Для выхода нажми Ctrl+C.\n")

#     try:
#         with sd.RawInputStream(
#             samplerate=SAMPLE_RATE,
#             blocksize=BLOCK_SIZE,
#             device=None,          # Микрофон по умолчанию
#             dtype="int16",
#             channels=1,
#             callback=audio_callback,
#         ):
#             while True:
#                 data = audio_queue.get,()

#                 # True означает: Vosk распознал законченную фразу.
#                 if recognizer.AcceptWaveform(data):
#                     result = json.loads(recognizer.Result())
#                     text = result.get("text", "").strip()

#                     if text:
#                         print(f"🎤 Распознано: {text}")

#                         if text in {"выход", "стоп", "завершить"}:
#                             speak(tts, "Завершаю работу.")
#                             break

#                         # Вместо повторения можно вызвать обработчик команд робота.
#                         speak(tts, text)

#     except KeyboardInterrupt:
#         print("\nОстановлено пользователем.")


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3

import json
import queue
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import sounddevice as sd
from vosk import Model, KaldiRecognizer


SAMPLE_RATE = 16000
BLOCK_SIZE = 8000


class VoiceNode(Node):
    def __init__(self):
        super().__init__('voice_node')

        # Издатель распознанного текста
        self.voice_pub = self.create_publisher(
            String,
            '/voice_command',
            10
        )

        self.get_logger().info('VoiceNode запущена. Слушаю микрофон...')

        # Очередь для аудио между callback и потоком распознавания
        self.audio_queue = queue.Queue()

        # Загрузка модели Vosk
        # Укажи путь к своей модели, например "vosk-model-small-ru-0.22"
        model_path = "vosk-model-small-ru-0.22"
        model = Model(model_path)

        self.recognizer = KaldiRecognizer(model, SAMPLE_RATE)
        self.recognizer.SetWords(True)

        # Запуск микрофона в отдельном потоке
        self.mic_thread = threading.Thread(
            target=self._run_microphone,
            daemon=True
        )
        self.mic_thread.start()

        # Основной цикл распознавания в фоне
        self.listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listen_thread.start()

    def _run_microphone(self):
        """Поток с RawInputStream, который кладёт аудио в audio_queue."""

        def audio_callback(indata, frames, time, status):
            if status:
                self.get_logger().warn(f"Статус звука: {status}")
            # indata — numpy-массив, преобразуем в байты
            self.audio_queue.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                device=None,  # микрофон по умолчанию
                dtype="int16",
                channels=1,
                callback=audio_callback,
            ):
                # Блокируем поток, пока поток не будет остановлен
                while rclpy.ok():
                    sd.sleep(100)
        except Exception as e:
            self.get_logger().error(f"Ошибка микрофона: {e}")

    def _listen_loop(self):
        """Поток, который читает аудио из очереди и передаёт в Vosk."""

        while rclpy.ok():
            try:
                data = self.audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            # True — Vosk считает, что фраза закончена
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()

                if text:
                    self.get_logger().info(f"🎤 Распознано: {text}")

                    # Публикация в ROS 2
                    msg = String()
                    msg.data = text
                    self.voice_pub.publish(msg)

                    # Опционально: команды остановки ноды
                    if text in {"выход", "стоп", "завершить"}:
                        self.get_logger().info("Получена команда остановки.")
                        # Можно вызвать shutdown, если нужно
                        # rclpy.shutdown()
                        # break


def main(args=None):
    rclpy.init(args=args)

    node = VoiceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()