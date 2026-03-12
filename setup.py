import setuptools

with open("README.md", "rb") as fh:
    long_description = fh.read().decode("utf-8")

setuptools.setup(
    name='pyflowchart',
    version='0.6.0',
    url='https://github.com/cdfmlr/pyflowchart',
    license='MIT',
    author='CDFMLR',
    author_email='cdfmlr@outlook.com',
    description='Python codes to Flowcharts.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
    install_requires=['astunparse; python_version < "3.9"', 'chardet'],
    entry_points={
        'console_scripts': [
            'pyflowchart=pyflowchart.__main__:cli',
        ],
    },
)
