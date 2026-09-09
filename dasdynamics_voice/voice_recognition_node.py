import os
import queue
import rclpy
import json
import threading

from rclpy.node import Node
from std_msgs.msg import String

import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoiceRecognitionNode (Node):
    def __init__(self):
        super().__init__("voice_recognition_node")

        voice_model_path = os.path.expanduser('~/SmartBox/voice_models/vosk-model-ru-0.22')
        recogniser_text_topic_name = '/recognized_text'
        self.sample_rate = 16000
        self.block_size = 8000

        self.audio_queue = queue.Queue()

        voice_model = Model(voice_model_path)

        self.voice_recognizer = KaldiRecognizer(voice_model, self.sample_rate)
        self.voice_recognizer.SetWords(True)

        self.microphone_thread = threading.Thread(
            target = self.microphone_callback,
            daemon = True
        )

        self.microphone_thread.start()

        self.listen_thread = threading.Thread(
            target = self.listen_loop,
            daemon = True
        )

        self.listen_thread.start()

        self.recognized_text_pub = self.create_publisher(
            String,
            recogniser_text_topic_name,
            10
        )

        self.get_logger().info('Recognition node is run')


    def microphone_callback(self):

        def audio_callback(indata, frames, time, status):
            if status:
                self.get_logger().warning(f'Received status: {status}')
            self.audio_queue.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate = self.sample_rate,
                blocksize = self.block_size,
                device = None,
                dtype = "int16",
                channels = 1,
                callback = audio_callback,
            ):

                while rclpy.ok():
                    sd.sleep(100)
        except Exception as e:
            self.get_logger().warning(f'Microphone error: {e}')


    def listen_loop(self):
        while rclpy.ok():
            try:
                data = self.audio_queue.get(timeout = 1.0)
            except queue.Empty:
                continue

            if self.voice_recognizer.AcceptWaveform(data):
                result = json.loads(self.voice_recognizer.Result())
                text = result.get("text", "").strip()

                if text:

                    msg = String()
                    msg.data = text
                    self.recognized_text_pub.publish(msg)


def main():
    rclpy.init()
    node = VoiceRecognitionNode()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()