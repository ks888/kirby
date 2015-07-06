
import os


def reset_kirby_env_vars():
    unset_list = ['KIRBY_CONFIG', 'KIRBY_ENABLE', 'KIRBY_SERVERSPEC_DIR', 'KIRBY_SERVERSPEC_CMD']
    for unset in unset_list:
        if unset in os.environ:
            del os.environ[unset]
