from setuptools import setup, find_packages

__author__ = 'Rahul Kumar Verma (rahulsaraf424@gmail.com)'

setup(
    name='drive_convert',
    version='0.1',
    description='Convert the files from google drive.',
    author='Rahul Kumar Verma',
    author_email='rahulsaraf424@gmail.com',
    license='Proprietary',
    packages=find_packages(),
    package_data={'': ['*.txt', '*.yaml']},
    include_package_data=True,
    zip_safe=False,
    project_url="https://github.com/rahulverma6212/google_drive_files_convert.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests==2.21.0',
        'google-api-python-client==1.7.8'
    ])
