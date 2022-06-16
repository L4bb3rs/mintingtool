#!/usr/bin/env python

from setuptools import setup

#with open("README.md", "rt") as fh:
#    long_description = fh.read()

dependencies = [
    "chia-blockchain@git+https://github.com/Chia-Network/chia-blockchain.git@release/1.4.0#62e261a5ba48f96ef8f2b26369c2e064a05ac0f9",
    "requests"
]

dev_dependencies = [
    "black",
]

setup(
    name="mintingtool",
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
