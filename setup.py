import pathlib
from setuptools import setup, find_packages
import time
import os
import pathlib

import cpmaxToolbox

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

VERSION = '.'.join(cpmaxToolbox.__version__.split(".")[:3])+"."+hex(int(time.time()))[2:]

init = pathlib.Path.cwd()/"cpmaxToolbox"/"__init__.py"

with open("temp", "w") as f_w, open(init, "r") as f_r:
    for line in f_r.readlines():
        if not "__version__" in line:
            f_w.write(line)
        else:
            f_w.write (f'__version__ = "{VERSION}"')

os.remove(init)
os.rename("temp", init)

classifiers = [
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Development Status :: 4 - Beta",
    "Topic :: Scientific/Engineering",
]

setup(
    name="cpmaxToolbox",
    version=VERSION,
    description="Toolbox for cp.max Rotortechnik GmbH & Co. KG",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/JRoseCPMax/cpmax_toolbox",
    author="Jonas Rose",
    author_email="j.rose@cpmax.com",
    license="GPLv3",
    python_requires='>=3.0',
    classifiers=classifiers,
    packages=find_packages(),
    include_package_data=True,
    install_requires=["pandas", "numpy", "rich"],
)