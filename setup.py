from setuptools import setup

version = '0.01'

setup(
    name='gotm_tools',
    packages=['gotm_tools'],
    version=version,
    description=("gotm_tools is a collection of various tools to speed up working with gotm"),
    author='Mike Bedington',
    author_email='mib@akvaplan.niva.no',
    url='https://github.com/mikebedington/gotm_tools.git',
    keywords=['gotm', 'ERSEM'],
    license='MIT',
    platforms='any',
    install_requires=['numpy', 'datetime', 'netcdf4', 'matplotlib'],
    classifiers=[]
)

