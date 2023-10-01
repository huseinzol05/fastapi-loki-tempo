import setuptools
import fastapi_loki_tempo

__packagename__ = 'fastapi-loki-tempo'


with open('requirements.txt') as fopen:
    req = list(filter(None, fopen.read().split('\n')))

setuptools.setup(
    name=__packagename__,
    packages=setuptools.find_packages(),
    version=fastapi_loki_tempo.__version__,
    python_requires='>=3.7',
    description='FastAPI boilerplate for Loki and Tempo.',
    author='huseinzol05',
    author_email='husein.zol05@gmail.com',
    url='https://github.com/huseinzol05/fastapi-loki-tempo',
    keywords=['fastapi', 'tempo', 'loki'],
    install_requires=req,
    license='MIT',
    classifiers=[
            'Programming Language :: Python :: 3.7',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Topic :: FastAPI',
    ],
)
