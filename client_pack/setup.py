from setuptools import setup, find_packages

setup(name="mess_client_march",
      version="0.7.0",
      description="mess_client",
      author="Ivan Necris45 Sizikov",
      author_email="Necris01@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
