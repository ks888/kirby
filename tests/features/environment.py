
import os


def before_all(context):
    os.chdir('tests/features/testdata/')

    os.environ['KIRBY_CONFIG'] = './kirby.conf'
