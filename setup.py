from setuptools import setup, find_packages

version = '0.1'

setup(name='test-har',
      version=version,
      description="Use HTTP Archive (HAR) files in Python tests",
      long_description="""\
""",
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
      test_suite='test_har.tests',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
