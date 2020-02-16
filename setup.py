from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
        name="sshfdpass",
        version="0.1",
        package_dir={"": "lib"},
        packages=find_packages("lib"),
        author="Gyorgy Pasztor",
        author_email="coruscant0@gmail.com",
        description="Helper script for ProxyUseFDPass option of openssh",
        long_description=long_description,
        keywords="ssh openssh proxyusefdpass",
        # PyYAML is not a hard dependency, just a suggestion
        #install_requires=['PyYAML'],
        url="https://github.com/pasztor/sshfdpass",
        license="MIT",
        project_urls={
            "Bug Tracker": "https://github.com/pasztor/sshfdpass/issues",
            "Documentation": "https://github.com/pasztor/sshfdpass/doc",
            "Source Code": "https://github.com/paszor/sshfdpass"
            },
        classifiers=[
            "License :: OSI Approved :: MIT License",
            "Environment :: Console",
            "Development Status :: 4 - Beta",
            "Environment :: Plugins",
            "Intended Audience :: Developers",
            "Intended Audience :: System Administrators",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Topic :: System :: Systems Administration",
            "Topic :: Terminals",
            ],
        entry_points={
            "console_scripts": [
                "sshfdpass = sshfdpass:run"
                ]
            }
        )
