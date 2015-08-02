
from behave import given, when, then
import os
import re
import subprocess
import time


@given(u'the target host is clean')
def step_impl(context):
    env_vars = ['KIRBY_CONFIG', 'KIRBY_ENABLE']
    for env_var in env_vars:
        if env_var in os.environ:
            del os.environ[env_var]

    for f in os.listdir('.'):
        if re.search('^dummy.*\.conf$', f):
            os.remove(f)

@given(u'env var is used instead of config file')
def step_impl(context):
    os.environ['KIRBY_ENABLE'] = 'yes'
    os.environ['KIRBY_SERVERSPEC_DIR'] = './'
    os.environ['KIRBY_SERVERSPEC_CMD'] = 'bundle exec rake spec'

@given(u'kirby is disabled')
def step_impl(context):
    os.environ['KIRBY_ENABLE'] = 'no'

@when(u'we run the playbook "{playbook}"')
def step_impl(context, playbook):
    cmd = 'ansible-playbook %s -i "localhost," -c local' % playbook

    start = time.time()
    try:
        context.cmd_output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        context.cmd_rc = 0
    except subprocess.CalledProcessError as ex:
        context.cmd_output = ex.output
        context.cmd_rc = ex.returncode
    elapsed = time.time() - start

    context.elapsed = elapsed

@then(u'stdout will include "{coverage}" as a coverage')
def step_impl(context, coverage):
    coverage = ' %s ' % coverage
    assert coverage in context.cmd_output

@then(u'stdout will not include "{coverage}" as a coverage')
def step_impl(context, coverage):
    coverage = ' %s ' % coverage
    assert coverage not in context.cmd_output


@then(u'stdout will not include "{warning}"')
def step_impl(context, warning):
    assert warning not in context.cmd_output

@then(u'stdout will include "{warning}"')
def step_impl(context, warning):
    assert warning in context.cmd_output

@then(u'elapsed time will be less than "{max_time}" seconds')
def step_impl(context, max_time):
    assert context.elapsed < float(max_time)
