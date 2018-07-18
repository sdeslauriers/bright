from setuptools import setup

setup(
    name='bright',
    version='0.0.0',
    packages=['bright'],
    url='',
    license='GPL-3.0',
    author='Samuel Deslauriers-Gauthier',
    author_email='sam.deslauriers@gmail.com',
    description='A Python package to render shining, blazing, beaming'
                'neuroscience images.',
    install_requires=['glfw', 'numpy', 'pyopengl', 'pyrr']
)
