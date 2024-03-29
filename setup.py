from setuptools import find_packages, setup
from channels import __version__

setup(
    name='bulb-channels',
    version=__version__,
    url='http://github.com/Bulb-Core/bulb-channels',
    author='LilaRest',
    author_email='mail@lila.rest',
    description="For of the django-channels project to make it compatible with bulb.",
    license='BSD',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        'Django>=2.2',
        'asgiref~=3.2',
        'daphne~=2.3',
    ],
    extras_require={
        'tests': [
            'pytest~=4.4',
            "pytest-django~=3.4",
            "pytest-asyncio~=0.10",
            "async_generator~=1.10",
            "async-timeout~=3.0",
            'coverage~=4.5',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
