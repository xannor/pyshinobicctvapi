from setuptools import find_packages, setup

setup(
    name="pyshinobicctvapi",
    packages=find_packages(include=["pyshinobicctvapi"]),
    version="0.1.0",
    description="Python Library for Shinobi CCTV API",
    author="Xannor Archouse",
    install_requires=["aiohttp"],
    setup_requires=["pytest-runner"],
    test_requires=["pytest"],
    test_suite="tests",
)