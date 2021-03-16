import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="firebaseloader",
    version="0.0.1",
    author="Poh Tze Ven",
    author_email="frasker@hotmail.com",
    description="A library to load python script to Firebase for execution in another system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chaosAD/FirebaseLoader",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyrebase'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System : Microsoft : Windows",
        "Operating System :: POSIX :: Linux",
    ],
)
