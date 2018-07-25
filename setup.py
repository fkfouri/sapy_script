import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sapy_script",
    version="0.0.1",
    author="fkfouri/mariotaddeucci",
    author_email="kfouri.fabio@gmail.com",
    description="Library to manipulate SAP by script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fkfouri/sapy_script",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows 7",
        "Operating System :: Windows 8",
        "Intended Audience :: Developers",
        "Intended Audience :: SAP :: Sap Script",
        ""
    ),
    keywords="SAP Script",
    install_requires=['pywin32==223', 'tqdm==4.20.0', 'wmi==1.4.9']

)