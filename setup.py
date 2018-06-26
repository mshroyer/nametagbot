from setuptools import setup

setup(
    name='nametagbot',
    version='0.0.1',
    packages=['nametagbot'],
    entry_points={
        'console_scripts': [
            'nametagbot-latex=nametagbot.cmd_latex:main',
            'nametagbot-updateroster=nametagbot.cmd_updateroster:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'responses'],
    test_suite='tests',
    url='',
    license='',
    author='Mark Shroyer',
    author_email='mark@shroyer.name',
    description='Discord nametags for NECSS!',
)
