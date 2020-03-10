from setuptools import setup, find_packages
import os

packages = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

f = open('README.md')
readme = f.read()
f.close()

f = open('LICENSE.txt')
license_text = f.read()
f.close()

setup(
    name='bw2landbalancer',
    version="0.1",
    packages=find_packages(),
    author="Pascal Lesage",
    author_email="pascal.lesage@polymtl.ca",
    install_requires=[
        'brightway2',
        'numpy',
        'pyprind',
        'presamples',
    ],
    url="https://gitlab.com/pascal.lesage/bw2landbalance",
    long_description=readme,
    long_description_content_type="text/markdown",
    description='Used to create balanced LCA land transformation exchange samples to override unbalanced samples in Brightway2.',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
