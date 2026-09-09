from setuptools import find_packages, setup

package_name = 'dasdynamics_voice'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
        install_requires=[
        'setuptools',
        'sounddevice',
        'vosk',
    ],
    zip_safe=False,
    maintainer='dasdynamics',
    maintainer_email='das-dev-md@mail.ru',
    description='A package for working with voice commands',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'voice_recognition_node = dasdynamics_voice.voice_recognition_node:main',
        ],
    },
)
