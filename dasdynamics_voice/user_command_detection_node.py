# import os
# import yaml
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
# from geometry_msgs.msg import PoseStamped
# from geometry_msgs.msg import PoseWithCovarianceStamped


class UserCommandDetectionNode (Node):
    def __init__(self):
        super().__init__("user_command_detection_node")

        self.user_command_topic_name = '/user_commands'
        self.recogniser_text_topic_name = '/recognized_text'

        self.save_waypoints_text_command = 'сохрани точку'
        self.save_waypoints_command = 'save_waypoint:'

        self.go_to_waypoint_text_command = 'отправляйся к точке'
        self.go_to_waypoint_command = 'go_to_waypoint:'


        self.recogniser_text_subscription = self.create_subscription(
            String,
            self.recogniser_text_topic_name,
            self.processing_text_callback,
            10, 
        )

        self.user_command_publisher = self.create_publisher(
            String,
            self.user_command_topic_name,
            10,
        )

        self.get_logger().info(f'UserCommandDetectionNode started. Listening on {self.recogniser_text_topic_name}')



    def processing_text_callback(self, msg:String):


        cmd = msg.data.strip()

        start_save_waypoints_text_command_position = cmd.find(self.save_waypoints_text_command)
        start_go_to_waypoint_text_command_position = cmd.find(self.go_to_waypoint_text_command)

        if start_save_waypoints_text_command_position > -1:
            start_symbol = start_save_waypoints_text_command_position + len(self.save_waypoints_text_command)
            text_for_find = cmd[start_symbol:].strip()
            find_word = text_for_find.split()[0] if text_for_find.split() else ""
            if not find_word:
                self.get_logger().warning('Received command is empty')
                return

            msg = String()
            msg.data = self.save_waypoints_command + find_word
            self.user_command_publisher.publish(msg)

            self.get_logger().info(f'Publishing command: {msg.data}')

        if start_go_to_waypoint_text_command_position > -1:
            start_symbol = start_go_to_waypoint_text_command_position + len(self.go_to_waypoint_text_command)
            text_for_find = cmd[start_symbol:].strip()
            find_word = text_for_find.split()[0] if text_for_find.split() else ""
            if not find_word:
                self.get_logger().warning('Received command is empty')
                return

            msg = String()
            msg.data = self.go_to_waypoint_command + find_word
            self.user_command_publisher.publish(msg)

            self.get_logger().info(f'Publishing command: {msg.data}')


def main():
    rclpy.init()
    node = UserCommandDetectionNode()
    rclpy.spin(node)
    node.destroy_node()


if __name__ == '__main__':
    main()
