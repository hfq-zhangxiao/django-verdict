import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-verdict',
    version='0.0.1',
    license='BSD License',  # example license
    description='A simple Django app to conduct permissions.',
    long_description=README,
    url='https://www.uxiu.info',
    author='mayor',
    author_email='finemayor@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.8.18',
        'django-cacheops==4.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8.18',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7.15',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)