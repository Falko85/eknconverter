# python setup.py --dry-run --verbose install

from distutils.core import setup

setup(
    name='ekn_convert',
    version='0.1.0',
    author='Falko Schmieder',
    author_email='',
    py_modules=['ekn_convert'],
    scripts=[],
    data_files=[],
    url='https://github.com/Falko85/eknconverter',
    license='MIT',
    description='class to read in My Gekko ekn files',
    long_description=open('README.md').read()
)
