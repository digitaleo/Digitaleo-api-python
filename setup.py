""" Digitaleo setup tools
"""

from setuptools import setup

setup(
    name='digitaleo',
    version='1.0.0',
    description='Digitaleo API client',
    url='https://github.com/digitaleo/Digitaleo-api-python',
    author='Digitaleo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='Digitaleo API client',
    packages=['digitaleo'],
    install_requires=['requests>=2.4.0', 'multidimensional_urlencode']
)
