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
		"Programming Language :: Other Scripting Engines",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 8",
        "Intended Audience :: Developers"
    ),
    keywords="SAP Script",
    install_requires=['pywin32==223', 'tqdm==4.20.0', 'wmi==1.4.9']

)