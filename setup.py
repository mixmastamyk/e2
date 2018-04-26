#!/usr/bin/env python
from distutils.core import setup

from .env import __version__ as version

# readme is needed at register time, not install time
try:
    with open('readme.rst') as f:
        long_description = f.read()
except IOError:
    long_description = ''


setup(
    name          = 'env',
    version       = version,
    description   = 'A simpler interface to environment variables.',
    author        = 'Mike Miller',
    author_email  = 'mixmastamyk@bitbucket.org',
    url           = 'https://github.com/mixmastamyk/env',
    license       = 'BSD',
    py_modules    = ['env'],

    long_description = long_description,
    classifiers     = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
