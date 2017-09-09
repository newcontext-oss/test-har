import os

from setuptools import setup, find_packages

version = '0.1'

tests_require = ['requests-mock', 'django-setuptest', 'djangorestframework']

setup(name='test-har',
      version=version,
      description="Use HTTP Archive (HAR) files in Python tests",
      long_description=open(os.path.join(
          os.path.dirname(__file__), 'README.rst')).read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords='testing test har',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='https://github.com/rpatterson/test-har',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='setuptest.setuptest.SetupTestSuite',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
