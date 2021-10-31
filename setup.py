import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ndw_chat",
    version="1.0.0",
    author="Johannes Bechberger",
    author_email="me@mostlynerdless.de",
    description="A viewer -> moderator -> host message system for streamed events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="<<< URL TO DOC WEBSITE OR GIT PROJECT >>>",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points={
        "console_scripts": [
            "ndw_chat_server=ndw_chat.main:cli",
        ]
    }
)
