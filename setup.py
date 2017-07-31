from setuptools import setup

setup(name = 'doit-reporter-xunit',
      description = 'doit reporter plugin - XML xunit output',
      version = '0.1.dev0',
      license = 'MIT',
      author = 'Eduardo Naufel Schettino',
      url = 'http://github.com/pydoit/doit-reporter-unit',
      py_modules=['doit_reporter_xunit'],
      entry_points = {
          'doit.REPORTER': [
              'xunit = doit_reporter_xunit:ReporterXunit'
          ]
      },
)
