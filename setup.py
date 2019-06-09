from setuptools import setup
import os
import textwrap

info = {}
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'couchbase', '__version__.py'), 'r') as f:
    exec(f.read(), info)

setup(
    name=info['__title__'],
    version=info['__version__'],
    author=info['__author__'],
    author_email=info['__author_email__'],
    maintainer=info['__maintainer__'],
    maintainer_email=info['__maintainer_email__'],
    packages=['couchbase',],
    url=info['__url__'],
    license=info['__license__'],
    description=info['__description__'],
    long_description=textwrap.dedent(open('README.md', 'r').read()),
    install_requires=[
                         'requests==2.14.2'
                     ],
    keywords=info['__keywords__'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)