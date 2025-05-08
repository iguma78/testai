"""
Setup script for the TestAI SDK package.
"""

from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="testai-sdk",
    version="0.1.0",
    author="Itzhak Guma",
    author_email="your.email@example.com",  # Replace with your email
    description="A Python SDK for monitoring OpenAI API calls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/testai-sdk",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.25.0"
    ],
    keywords="openai, api, monitoring, sdk, ai, gpt",
)
