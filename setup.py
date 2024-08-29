from setuptools import setup, find_packages

setup(
    name='hexalate',
    version='0.1.0',
    description='A package for generating hexagonal tessellations',
    author='James Campbell',
    author_email='james@jamescampbell.us',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'hexalate = hexalate.__main__:main',  # Change this line
        ],
    },
)
