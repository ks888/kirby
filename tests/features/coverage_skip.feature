Feature: Coverage Skip
    As a web operator
    I want to remove setup/cleanup tasks from coverage
    Because tests are not necessary for these tasks

    Scenario: Remove a task from coverage
        Given the target host is clean
        When we run the playbook "2tasks_2skipped.yml"
        Then stdout will include "0 of 0 tasks are tested"
        And stdout will not include "WARNING: serverspec"

    Scenario: Lots of skipped tasks (use with_seq)
        Given the target host is clean
        When we run the playbook "30tasks_30skipped_with_seq.yml"
        Then elapsed time will be less than "20.0" seconds

    Scenario: Lots of skipped tasks (not use with_seq)
        Given the target host is clean
        When we run the playbook "30tasks_30skipped.yml"
        Then elapsed time will be less than "20.0" seconds
