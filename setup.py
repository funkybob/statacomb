
from setuptools import setup, find_packages

setup(
    name='statacomb',
    version='0.0.1',
    description='A simple stats gather/display app using PG JSON field.',
    author='Curtis Maloney',
    author_email='curtis@tinbrain.net',
    url='http://github.com/funkybob/statacomb/',
    packages=find_packages(),
    package_data={
        'statacomb.web': ['templates/*'],
    },
    zip_safe=False,
    install_requires=[
        'psycopg2>=2.6',
        'antfarm==0.0.3',
    ],
)
