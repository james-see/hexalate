from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='hexalate',
    version='0.2.1',
    description='A package for generating hexagonal tessellations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='James Campbell',
    author_email='james@jamescampbell.us',
    url='https://github.com/james-see/hexalate',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'hexalate = hexalate.__main__:main',
        ],
    },
)
