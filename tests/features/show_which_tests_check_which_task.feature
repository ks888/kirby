Feature: Show Which Tests Check which Task
    As a web operator
    I want to know that which test checks which task
    Because often it is unclear that why a task is regarded as tested

    Scenario: Show which
        Given the target host is clean
        When we run the playbook "1task_1changed.yml"
        Then stdout will include "- rspec"

    Scenario: Not show which
        Given the target host is clean
        When we run the playbook "1task_1changed_not_tested.yml"
        Then stdout will not include "- rspec"
