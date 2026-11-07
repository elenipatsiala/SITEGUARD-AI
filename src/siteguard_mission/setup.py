from setuptools import find_packages, setup

package_name = 'siteguard_mission'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='eleni',
    maintainer_email='eleni@todo.todo',
    description='SITEGUARD-AI ROS 2 Mission Manager',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_manager = siteguard_mission.mission_manager:main',
            'hazard_detector = siteguard_mission.hazard_detector:main',
            'dashboard_bridge = siteguard_mission.dashboard_bridge:main',
            'telemetry_bridge = siteguard_mission.telemetry_bridge:main',
        ],
    },
)
