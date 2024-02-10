from setuptools import setup, Extension
import pybind11
import sys

include_dirs = pybind11.get_include()

extra_compile_args = []
if sys.platform == 'win32':
    extra_compile_args = ['/std:c++17']
else:
    extra_compile_args = ['-std=c++17']

ext_modules = [
    Extension(
        'PngDescriptionDLL',
        ['PngDescriptionDLL.cpp', 'PngDescriptionManager.cpp'],
        include_dirs=[include_dirs],
        language='c++',
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name='PngDescriptionManager',
    version='0.1',
    ext_modules=ext_modules,
)