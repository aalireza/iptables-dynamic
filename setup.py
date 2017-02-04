from setuptools import setup
from os import path
import codecs
import ConfigParser

here = path.abspath(path.dirname(__file__))
meta_parser = ConfigParser.RawConfigParser()
meta_parser.read(path.join(here, 'META.txt'))

with codecs.open(path.join(here, 'README.rst'), "r") as f:
    long_description = f.read()


setup(
    name=meta_parser.get("Program", "Name"),
    version=meta_parser.get("Program", "Version"),
    description=meta_parser.get("Program", "Description"),
    long_description=long_description,
    license=meta_parser.get("Program", "License"),
    author=meta_parser.get("Copyright", "Author_Name"),
    author_email=meta_parser.get("Copyright", "Author_Email"),
    packages=["iptables_dynamic"],
    url=meta_parser.get("Program", "URL"),
    download_url=(
        "{}/tarball/{}".format(
            meta_parser.get("Program", "URL"),
            meta_parser.get("Program", "TAG"),
        )
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking :: Firewalls",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords=["iptables", "save chain", "restore chain"],
    entry_points={
          'console_scripts': [
              'iptables-dynamic=iptables_dynamic:iptables_dynamic',
              'ip6tables-dynamic=iptables_dynamic:ip6tables_dynamic',
          ],
      },
)
