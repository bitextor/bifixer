#!/usr/bin/env python

import setuptools
import subprocess
import os.path

if __name__=="__main__":
    with open("README.md", "r") as fh:
        long_description = fh.read()
    with open("requirements.txt") as rf:
        requirements = rf.read().splitlines()
    with open("optional-requirements.txt") as ef:
        extras_requirements = ef.read().splitlines()

    setuptools.setup(
        name="bifixer",
        version="0.4",
        install_requires=requirements,
        extras_require={"loomchild": extras_requirements},
        license="GNU General Public License v3.0",
        author="Prompsit Language Engineering",
        author_email="info@prompsit.com",
        description="Tool to fix bitexts and tag near-duplicates for removal",
        maintainer="Marta Bañon",
        maintainer_email="mbanon@prompsit.com",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/bitextor/bifixer",
        packages=["bifixer"],
        package_data={"bifixer": ["replacements/*"]},
        classifiers=[
            "Environment :: Console",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: POSIX :: Linux",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Text Processing :: Linguistic",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Text Processing :: Filters"
        ],
        project_urls={
            "Bifixer on GitHub": "https://github.com/bitextor/bifixer",
            "Prompsit Language Engineering": "http://www.prompsit.com",
            "Paracrawl": "https://paracrawl.eu/"
             },
        scripts=["scripts/bifixer"]
    )
