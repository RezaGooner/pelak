from setuptools import setup, find_packages

setup(
    name='pelak',
    version='1.0.0',
    description='ابزاري کاربردي براي پلاک هاي ايراني',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='RezaGooner',
    author_email='RezaAsadiProgrammer@Gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    package_data={'pelak': ['data/*.png', 'data/*.ttf', 'data/*.txt']},
    install_requires=[
        'pillow>=10.0.0',
    ],
    python_requires='>=3.7',
    url='https://github.com/RezaGooner/pelak',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
