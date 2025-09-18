#!/usr/bin/env python3
"""
CUDA Sentinel - GPU Health Monitoring and Benchmarking Tool
Setup configuration for Python package
"""

from setuptools import setup, find_packages
import os

# Read README for long description
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'CUDA Sentinel - GPU Health Monitoring Tool'

# Read requirements
try:
    with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'click>=8.0.0',
        'numpy>=1.21.0',
        'nvidia-ml-py>=11.495.46',
        'pandas>=1.5.0',
        'prometheus-client>=0.15.0',
        'psutil>=5.9.0',
        'pydantic>=2.0.0',
        'pynvml>=11.4.1',
        'pyyaml>=6.0',
        'requests>=2.28.0',
        'rich>=12.0.0',
    ]

setup(
    name='cuda-sentinel',
    version='0.1.0',
    description='GPU Health Monitoring and Benchmarking Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # Author info
    author='CUDA Sentinel Team',
    author_email='info@cuda-sentinel.dev',
    
    # URLs
    url='https://github.com/sakiphan/cuda-sentinel',
    project_urls={
        'Bug Reports': 'https://github.com/sakiphan/cuda-sentinel/issues',
        'Source': 'https://github.com/sakiphan/cuda-sentinel',
        'Documentation': 'https://github.com/sakiphan/cuda-sentinel#readme',
    },
    
    # Package info
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=requirements,
    
    # Optional dependencies for different use cases
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991',
        ],
        'benchmark': [
            'cupy-cuda12x>=12.0.0',  # For CUDA 12.x
            'torch>=1.13.0',
        ],
        'visualize': [
            'matplotlib>=3.5.0',
            'seaborn>=0.11.0',
            'plotly>=5.0.0',
        ],
    },
    
    # Entry points for CLI commands
    entry_points={
        'console_scripts': [
            'cuda-sentinel=cuda_sentinel.cli.main:cli',
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Hardware',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
    ],
    
    # Keywords
    keywords='gpu cuda nvidia monitoring health benchmark nvml',
    
    # Include additional files
    include_package_data=True,
    package_data={
        'cuda_sentinel': [
            'config/*.yml',
            'templates/*.json',
        ],
    },
)
