from setuptools import setup, find_packages
import pathlib

current_dir = pathlib.Path(__file__).parent.resolve()
long_description = (current_dir / 'README.md').read_text(encoding='utf-8')

setup(
    name="ssyt",
    version="0.1dev",
    description='Systema Sociedad y Territorio',
    long_description=long_description,
    author='CEEU - UNSAM',
    author_email='fcatalano@unsam.edu.ar',
    url='https://github.com/PyMap/ssyt',
    classifiers=[
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'google-cloud-bigquery >= 1.9.0',
        'google-cloud-bigquery-storage >= 2.9.1',
        'google-cloud-bigquery[bqstorage,pandas]',
        'numpy >= 1.21.3',
        'pandas >= 1.3.4',
        'streamlit >= 1.1.0',
        'matplotlib >= 3.4.3',
    ]
)
