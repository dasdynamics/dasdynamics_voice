## dasdynamics_voice
Репозиторий содержит ROS 2-пакет с нодами для обработки голосовых команд пользователя.

 - 'voice_recognition_node' - получает аудиопоток из стандартного микрофона робота и превращает его в текст с помощью библиотеки vosk. Происходит это все offline. Распознанные слова отправляет в топик '/recognized_text'.
 Примечание: для работы нужна голосовая модель которую можно скачать с официального сайта:
 https://alphacephei.com/vosk/models

 - 'user_command_detection_node' - содержит в себе список комманд пользователя, который робот способен выполнить. Читает данные из топика '/recognized_text' сверяет их со списком существующих команд, и если находит таковые - отправляет команды в топик из которого робот получает команды.

 Примечание: на данный момент работа этого узла плохо оптимизирована. Вндутся работы по оптимизации и добавлении нового функционала.




 sudo apt-get update
sudo apt-get install python3-pyaudio
sudo apt update
sudo apt install -y portaudio19-dev libasound2-dev build-essential

sudo apt update
sudo apt install python3-pip
sudo apt install python3-sounddevice
pip3 install --break-system-packages vosk