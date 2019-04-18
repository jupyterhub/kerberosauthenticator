import versioneer
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='jupyterhub-kerberosauthenticator',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='BSD',
    maintainer='Jim Crist',
    maintainer_email='jiminy.crist@gmail.com',
    description='A JupyterHub authenticator using Kerberos',
    long_description=long_description,
    url='http://github.com/jcrist/kerberosauthenticator',
    project_urls={
        'Source': 'https://github.com/jcrist/kerberosauthenticator',
        'Issue Tracker': 'https://github.com/jcrist/kerberosauthenticator/issues'
    },
    keywords='jupyter contentsmanager HDFS Hadoop',
    classifiers=[
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Distributed Computing',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    packages=['kerberosauthenticator'],
    python_requires='>=3.5',
    install_requires=[
        'jupyterhub',
        'pykerberos;platform_system!="Windows"',
        'winkerberos;platform_system=="Windows"',
    ],
    include_package_data=True
)
