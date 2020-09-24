
import setuptools

setuptools.setup(
    name="canopy",
    version="0.0.1",
    author="billymillions",
    author_email="wmschwa@gmail.com",
    description="Small library for schema parsing",
    url="https://github.com/billymillions/canopy",
    packages=["canopy"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
