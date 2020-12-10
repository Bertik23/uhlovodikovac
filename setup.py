import setuptools
import uhlovodikovac

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=uhlovodikovac.__title__, # Replace with your own username
    version=uhlovodikovac.__version__,
    author=uhlovodikovac.__author__,
    author_email="bertikxxiii@gmail.com",
    description="Package for Hydrocarbon to Image conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bertik23/uhlovodikovac",
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        "Pillow ~= 8.0.0",
        "numpy ~= 1.17.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    package_dir={"":"src"},
    package_data={'uhlovodikovac': ['hydrocarbons.jsonc']}
)