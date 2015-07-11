Feature: Get Coverage
    As a web operator
    I want to know the test coverage of Ansible code
    Because tests may be insufficient

    Scenario: Coverage 100%
        Given the target host is clean
        When we run the playbook "4tasks_2changed.yml"
        Then stdout will include "100%" as a coverage
        And stdout will not include "WARNING: serverspec"

    Scenario: Coverage 50% and serverspec failed
        Given the target host is clean
        When we run the playbook "2tasks_2changed.yml"
        Then stdout will include "50%" as a coverage
        And stdout will include "WARNING: serverspec"

    Scenario: No changed tasks
        Given the target host is clean
        When we run the playbook "1task_0changed.yml"
        Then stdout will include "0%" as a coverage
        And stdout will include "WARNING: serverspec"

    Scenario: Ansible failed
        Given the target host is clean
        When we run the playbook "2tasks_1failed.yml"
        Then stdout will include "100%" as a coverage
        And stdout will include "WARNING: serverspec"

    Scenario: Use env var
        Given the target host is clean
        And env var is used instead of config file
        When we run the playbook "4tasks_2changed.yml"
        Then stdout will include "100%" as a coverage
        And stdout will not include "WARNING: serverspec"

    Scenario: Disable kirby
        Given the target host is clean
        And kirby is disabled
        When we run the playbook "4tasks_2changed.yml"
        Then stdout will not include "100%" as a coverage
        And stdout will not include "WARNING: serverspec"
