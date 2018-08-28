from setuptools import setup, find_packages
import asf

setup(
    name='asf',
    version=asf.__version__,
    long_description=asf.__description__,
    url=asf.__url__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'qquery>=0.0.1'
    ]
)
