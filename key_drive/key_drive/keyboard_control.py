import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import select
import termios
import tty

MAX_ANGLE = 0.5
SPEED_STEP = 0.1

msg = """
LIMO Keyboard Controller
---------------------------
Speed Control:
   w : Increase speed
   s : Decrease speed
   x : Force stop (speed = 0)

Steering Control (On/Off max angle):
   a : Max Left
   d : Max Right
   c : Center Steering

CTRL-C to quit
"""

class KeyboardControlNode(Node):
    def __init__(self):
        super().__init__('keyboard_control')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.speed = 0.0
        self.steering = 0.0
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info(msg)

    def getKey(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def timer_callback(self):
        key = self.getKey()
        if key != '':
            if key == 'w':
                self.speed += SPEED_STEP
                self.get_logger().info(f"Speed increased: {self.speed:.2f}")
            elif key == 's':
                self.speed -= SPEED_STEP
                self.get_logger().info(f"Speed decreased: {self.speed:.2f}")
            elif key == 'x':
                self.speed = 0.0
                self.get_logger().info(f"Speed stopped: {self.speed:.2f}")
            elif key == 'a':
                self.steering = MAX_ANGLE
                self.get_logger().info("Steering: Max Left")
            elif key == 'd':
                self.steering = -MAX_ANGLE
                self.get_logger().info("Steering: Max Right")
            elif key == 'c':
                self.steering = 0.0
                self.get_logger().info("Steering: Center")
            elif key == '\x03': # CTRL-C
                self.speed = 0.0
                self.steering = 0.0
                self.publish_twist()
                sys.exit(0)

        self.publish_twist()

    def publish_twist(self):
        twist = Twist()
        twist.linear.x = self.speed
        twist.angular.z = self.steering
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardControlNode()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    except Exception as e:
        node.get_logger().error(f"Error: {e}")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
