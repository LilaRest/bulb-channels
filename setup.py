from setuptools import find_packages, setup
from channels import __version__

setup(
    name='channels',
    version=__version__,
    url='http://github.com/django/channels',
    author='Django Software Foundation',
    author_email='foundation@djangoproject.com',
    description="Brings async, event-driven capabilities to Django. Django 1.11 and up only.",
    license='BSD',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'Django>=1.11',
        'asgiref~=2.0',
        'daphne~=2.0',
    ],
    extras_require={
        'tests': [
            'pytest~=3.3',
            'coverage~=4.4',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
