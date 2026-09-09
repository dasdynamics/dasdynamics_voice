import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # --- Параметры для изменения ---
    voice_pkg_name = 'dasdynamics_voice'
    # --- --- --- --- --- --- --- ---


    user_command_detection_node = Node(
        package = voice_pkg_name,
        executable = 'user_command_detection_node',
        name = 'user_command_detection',
        output = 'screen',
    )

    voice_recognition_node = Node(
        package = voice_pkg_name,
        executable = 'voice_recognition_node',
        name = 'voice_recognition',
        output = 'screen',
    )


    ld = LaunchDescription()

    ld.add_action(user_command_detection_node)
    ld.add_action(voice_recognition_node)

    return ld