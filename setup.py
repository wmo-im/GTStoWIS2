
import codecs
import os
import re
import sys

from setuptools import find_packages
from distutils.core import setup

import GTStoWIS2

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()

packages=find_packages()
print("packages = %s" % packages)

setup(
    name='wmo-im-GTS2WIS2',
    version=GTStoWIS2.__version__,
    description='Convert GTS AHL to WIS2 topic tree',
    long_description=(read('README.rst')),
    url='https://github.com/wmo-im/GTStoWIS2',
    license='GPLv3',
    author='WMO information management / metadata team',
    author_email='peter.silva.wmo@gmail.com', # for now... change later...
    
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: File Sharing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = [ 'GTStoWIS2' ],
    include_package_data=True,
)
    
    

