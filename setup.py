from setuptools import setup

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='xtiff',
    version='0.6.2',
    description='A tiny Python 3 library for writing multi-channel TIFF stacks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BodenmillerGroup/xtiff',
    author='Jonas Windhager',
    author_email='jonas.windhager@uzh.ch',
    license='MIT',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords='xarray ome tiff',
    project_urls={
        'Source': 'https://github.com/BodenmillerGroup/xtiff',
        'Tracker': 'https://github.com/BodenmillerGroup/xtiff/issues',
    },
    py_modules=['xtiff'],
    install_requires=[
        'numpy',
        'tifffile>=2020.6.3,!=2020.7.17',
    ],
    extras_require={
        'xtiff_support': ['xtiff'],
    },
    python_requires='>=3.7',
    zip_safe=True,
)
