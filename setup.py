"""
Installs the sequencebuilder package
"""

from setuptools import setup, find_packages
from pathlib import Path

import versioneer

readme_file_path = Path(__file__).absolute().parent / "README.md"

required_packages = ['qcodes>=0.21.0',
                    'qdev_wrappers @ git+https://github.com/qdev-dk/qdev-wrappers@master#egg=qdev_wrappers',
                    'PyQt5',
                    'scipy']
package_data = {"sequencebuilder": ["conf/telemetry.ini"] }


setup(
    name="sequencebuilder",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    python_requires=">=3.7",
    install_requires=required_packages,
    author= "Rasmus Bjerregaard Christensen",
    author_email="rbcmail@gmail.com",
    description="build broadbean sequences and measure by Alazar",
    long_description=readme_file_path.open().read(),
    long_description_content_type="text/markdown",
    license="",
    package_data=package_data,
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
    ],
)
