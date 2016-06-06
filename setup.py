from setuptools import setup

setup(
    name='flask-tracking',
    version='0.1',
    url='http://github.com/closeio/flask-tracking',
    license='MIT',
    description='Tracking app for Flask that logs HTTP request and response information in a capped MongoDB collection',
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
    packages=[
        'flask_tracking',
    ],
)
