from setuptools import setup

VERSION = '0.1.0'
REPO = 'https://github.com/bitlang/cssquery'

setup(
    name='cssquery',
    packages=['cssquery'],
    version=VERSION,
    description='Query objects with CSS selectors',
    author='Josh Junon',
    author_email='josh@junon.me',
    url=REPO,
    download_url='{}/archive/{}.tar.gz'.format(REPO, VERSION),
    keywords=['css', 'select', 'query', 'selectors', 'selector', 'object', 'regular', 'xpath'],
    classifiers=[],
    install_requires=['flexicon']
)
