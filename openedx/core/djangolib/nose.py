"""
Utilities related to nose.
"""
from django.core.management import call_command

import django_nose


class NoseTestSuiteRunner(django_nose.NoseTestSuiteRunner):
    """Custom NoseTestSuiteRunner."""

    def setup_databases(self):
        """ Setup databases and then flush to remove data added by migrations. """
        return_value = super(NoseTestSuiteRunner, self).setup_databases()
        call_command('flush', verbosity=0, interactive=False)
        return return_value
