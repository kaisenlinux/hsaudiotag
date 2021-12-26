from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
]

LONG_DESC = open('README', 'rt').read() + '\n\n' + open('CHANGES', 'rt').read()

setup(
    name='hsaudiotag3k',
    version='1.1.3',
    author='Hardcoded Software',
    author_email='hsoft@hardcoded.net',
    packages=['hsaudiotag'],
    scripts=[],
    install_requires=[],
    url='http://hg.hardcoded.net/hsaudiotag/',
    license='BSD License',
    description='Read metdata (tags) of mp3, mp4, wma, ogg, flac and aiff files.',
    long_description=LONG_DESC,
    classifiers=CLASSIFIERS,
)