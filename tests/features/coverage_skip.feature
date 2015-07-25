Feature: Coverage Skip
    As a web operator
    I want to remove setup/cleanup tasks from coverage
    Because tests are not necessary for these tasks

    Scenario: Remove a task from coverage
        Given the target host is clean
        When we run the playbook "2tasks_2skipped.yml"
        Then stdout will include "0 of 0 tasks are tested"
        And stdout will not include "WARNING: serverspec"
