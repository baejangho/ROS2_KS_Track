# Autor: Zhui Li
# E-Mail: lz554113510@gmail.com
# Company: Institut für Intermodale Transport- und Logistiksysteme in Technische Universität Braunschweig
# Description: Diese py-Datei basiert auf Regeln und definiert Funktionen durch python,
# um den Launch der Simulation in Gazebo zu ermöglichen. Danach mit der Simulation in Gazebo kann man die weitere
# Forschung arbeiten. Diese Launch-Datei dient zu Ackermann-Type.

import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():

    # definiert Path für Modell
    package_name = 'limo_car'
    # world_file_path = '/usr/share/gazebo-11/worlds/empty.world'
    world_file_path = 'worlds/KS_Track.world'
    # rviz_path = 'rviz/gazebo.rviz'

    pkg_path = os.path.join(get_package_share_directory(package_name))
    world_path = os.path.join(pkg_path, world_file_path)
    # default_rviz_config_path = os.path.join(pkg_path, rviz_path)

    # rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=str(default_rviz_config_path),
    #                                  description='Absolute path to rviz config file')
    # rviz_node = Node(
    #     package='rviz2',
    #     executable='rviz2',
    #     name='rviz2',
    #     output='screen',
    #     arguments=['-d', LaunchConfiguration('rvizconfig')],
    # )

    # Position dafür, wo die Modelle herstellt werden
    spawn_x_val = '-0.5'
    spawn_y_val = '-2.7'
    spawn_z_val = '-0.005'
    spawn_yaw_val = '0.0'

    # Set GAZEBO_MODEL_PATH so Gazebo can find package:// meshes
    set_env = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=os.path.join(get_package_share_directory(package_name), '..')
    )


    mbot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch', 'ackermann.launch.py'
        )]), launch_arguments={'use_sim_time': 'true', 'world': world_path}.items()
    )

    # # Einbindung der Gazebo-Startdatei, die im gazebo_ros-Paket enthalten ist
    # gazebo = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
    # )
    gzclient = ExecuteProcess(
    cmd=['gzclient'],
    output='screen'
    )

    # Gazebo 실행 (gzserver + gzclient를 직접 실행해서 eol gui 플러그인을 피함)
    gzserver = ExecuteProcess(
        cmd=[
            'gzserver',
            world_path,   # pkg_path와 합쳐진 올바른 절대 경로 사용
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so',
            '-s', 'libgazebo_ros_force_system.so',
            '-s', 'libgazebo_ros_state.so',
        ],
        output='screen'
    )

    # ✅ 중요: gzclient를 기본으로 실행 (문제의 --gui-client-plugin=libgazebo_ros_eol_gui.so 를 안 씀)
    gzclient = ExecuteProcess(
        cmd=['gzclient'],
        output='screen'
    )

    # laufen ein leere node aus den gazebo_ros package
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'mbot',
                                   '-x', spawn_x_val,
                                   '-y', spawn_y_val,
                                   '-z', spawn_z_val,
                                   '-Y', spawn_yaw_val],
                        output='screen')
    spawn_delayed = TimerAction(period=4.0, actions=[spawn_entity])

    return LaunchDescription([
    set_env,
    mbot,
    gzserver,
    gzclient,
    spawn_delayed,
])