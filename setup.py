import sys
from Cython.Build import cythonize
from setuptools import setup

setup(
    ext_modules=cythonize(
        "main.py",  # Tên file .py cần đổi sang .pyd
        compiler_directives={"language_level": "3"},
    )
)