#!/usr/bin/env python3
import json
import queue
import sys
from pathlib import Path

import sounddevice as sd
from vosk import KaldiRecognizer, Model
import pyttsx3

MODEL_PATH = Path("vosk-model-ru-0.22")
SAMPLE_RATE = 16_000
BLOCK_SIZE = 8_000

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    """Получает необработанный звук из потока микрофона."""
    if status:
        print(f"Audio status: {status}", file=sys.stderr)

    audio_queue.put(bytes(indata))


def create_tts():
    engine = pyttsx3.init()

    # Скорость речи: eSpeak хорошо звучит примерно в диапазоне 130–170.
    engine.setProperty("voice", "russian+f2")
    engine.setProperty("rate", 109)
    engine.setProperty("volume", 1.0)

    return engine


def speak(engine, text):
    print(f"🔊 Повторяю: {text}")
    engine.say(text)
    engine.runAndWait()


def main():
    if not MODEL_PATH.is_dir():
        print(
            f"Не найдена модель Vosk: {MODEL_PATH.resolve()}\n"
            "Скачай и распакуй русскую модель, затем проверь MODEL_PATH."
        )
        sys.exit(1)

    print("Загружаю локальную модель Vosk…")


    model = Model(str(MODEL_PATH))
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetWords(True)

    tts = create_tts()

    print("\nОфлайн-голосовой повторитель запущен.")
    print("Говори в микрофон. Для выхода нажми Ctrl+C.\n")

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=None,          # Микрофон по умолчанию
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            while True:
                data = audio_queue.get,()

                # True означает: Vosk распознал законченную фразу.
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()

                    if text:
                        print(f"🎤 Распознано: {text}")

                        if text in {"выход", "стоп", "завершить"}:
                            speak(tts, "Завершаю работу.")
                            break

                        # Вместо повторения можно вызвать обработчик команд робота.
                        speak(tts, text)

    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")


if __name__ == "__main__":
    main()