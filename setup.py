from setuptools import setup

setup(
    name='nametagbot',
    version='0.0.1',
    packages=['nametagbot'],
    entry_points={
        'console_scripts': [
            'nametagbot-updateroster=nametagbot.cmd_updateroster:main',
        ],
    },
    test_suite='tests',
    url='',
    license='',
    author='Mark Shroyer',
    author_email='mark@shroyer.name',
    description='Discord nametags for NECSS!',
)
