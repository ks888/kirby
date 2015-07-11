
import os


def before_all(context):
    os.chdir('tests/features/testdata/')

    if 'KIRBY_CONFIG' in os.environ:
        del os.environ['KIRBY_CONFIG']
