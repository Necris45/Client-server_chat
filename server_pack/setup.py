from setuptools import setup, find_packages

setup(name="mess_server_march_26",
      version="0.5.1",
      description="mess_server",
      author="Ivan Necris45 Sizikov",
      author_email="Necris01@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
