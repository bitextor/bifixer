#!/usr/bin/env python

import setuptools
import subprocess
import os.path
import shutil
from sys import argv

def compile_loomchild(current_path):
    jars = ["activation-1.1.1.jar",  "commons-cli-1.2.jar",  "commons-logging-1.1.1.jar",
        "gson-2.8.0.jar",  "jaxb-api-2.3.0.jar",  "jaxb-core-2.3.0.jar",
        "jaxb-impl-2.3.0.jar",  "junit-4.1.jar",  "segment-2.0.2-SNAPSHOT.jar",
        "segment-2.0.2-SNAPSHOT-tests.jar",  "segment-ui-2.0.2-SNAPSHOT.jar"]

    all_compiled = True
    for f in jars:
        if not os.path.isfile(os.path.join(current_path, "bifixer/data/segment-2.0.2-SNAPSHOT/lib", f)):
            all_compiled = False
            break

    if not all_compiled:
        subprocess.check_call(["mvn", "clean", "install"], cwd=os.path.join(current_path, "segment/segment"))
        subprocess.check_call(["mvn", "clean", "install"], cwd=os.path.join(current_path, "segment/segment-ui"))
        subprocess.check_call(["unzip", "-o", os.path.join(current_path, "segment/segment-ui/target/segment-2.0.2-SNAPSHOT.zip"), 
            "segment-2.0.2-SNAPSHOT/lib/*", "-d", os.path.join(current_path, "bifixer/data")])

    shutil.copytree(os.path.join(current_path, "segment/srx"), os.path.join(current_path, "bifixer/data/srx"), dirs_exist_ok=True)

if __name__=="__main__":
    with open("README.md", "r") as fh:
        long_description = fh.read()
    with open("requirements.txt") as rf:
        requirements = rf.read().splitlines()

    package_data_list=["replacements/*"] 

    if "--install-loomchild" in argv:
        argv.remove("--install-loomchild")
        compile_loomchild(os.path.dirname(os.path.abspath(__file__)))
        package_data_list.append("data/segment-2.0.2-SNAPSHOT/lib/*.jar")
        package_data_list.append("data/srx/*.srx")

    setuptools.setup(
        name="bifixer",
        #version="",
        install_requires=requirements,
        license="GNU General Public License v3.0",
        author="Prompsit Language Engineering",
        #author_email="",
        #maintainer="",
        #maintainer_email="",
        #description="",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/bitextor/bifixer",
        packages=["bifixer"],
        package_data={"bifixer": package_data_list},
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
