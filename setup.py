#!/usr/bin/env python

from setuptools import setup

#with open("README.md", "rt") as fh:
#    long_description = fh.read()

dependencies = [
    "requests",
    #"chia-blockchain@git+https://github.com/Chia-Network/chia-blockchain.git@release/1.5.0#787e96b8edc6ed95ca7a6d6ade115a62e6bff672",
]

dev_dependencies = [
    "black",
]

setup(
    name="NFTr_minting_tool",
    version="0.0.1",
    author="nftr",
    setup_requires=["setuptools_scm"],
    install_requires=dependencies,
    extras_require=dict(
        dev=dev_dependencies,
    ),
    project_urls={
        "Bug Reports": "https://github.com/nftr/mintingtool",
        "Source": "https://github.com/nftr/mintingtool",
    },
)
