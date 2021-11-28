import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="exelog",
    version="0.0.1",
    author="Souvik Pratiher",
    author_email="spratiher9@gmail.com",
    description="Enabling meticulous logging for Spark Applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Spratiher9/Exelog",
    py_modules=["exelog"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        "atomicwrites",
        "attrs",
        "colorama",
        "iniconfig",
        "packaging",
        "pluggy",
        "py",
        "py4j",
        "pyparsing",
        "pyspark",
        "pytest",
        "toml"
    ]
)
