[![wercker status](https://app.wercker.com/status/aee56ee616161469fb8e0f50fb4a6047/s/master "wercker status")](https://app.wercker.com/project/bykey/aee56ee616161469fb8e0f50fb4a6047)

# Kirby

![Greeting](http://i.imgur.com/0QkGgYC.png)

Code Coverage Tool for Ansible

## Description

It is usual to measure the code coverage for your source code written in python, Java, and so on. On the other hand, we usually do not measure the coverage for an Ansible playbook. Kirby is the tool to support this.

Here is the example. This is the playbook to be tested. There are 2 tasks.

```bash
~/src/kirby_demo% cat create_2dirs.yml
---
- hosts: localhost
  gather_facts: no
  tasks:
    - name: create dir1
      file: path=./dir1 state=directory

    - name: create dir2
      file: path=./dir2 state=directory
```

Here is the [Serverspec](http://serverspec.org/) test. There is 1 test for the first task (create dir1).

```bash
~/src/kirby_demo% cat spec/localhost/sample_spec.rb 
require 'spec_helper'

describe file('./dir1') do
  it { should be_directory }
end
```

Now, run the playbook. Kirby shows you the code coverage.

```bash
~/src/kirby_demo% ansible-playbook create_2dirs.yml -i "localhost," -c local

PLAY [localhost] ************************************************************** 

TASK: [create dir1] *********************************************************** 
changed: [localhost]
tested by: 
- rspec ./spec/localhost/sample_spec.rb:4 # File "./dir1" should be directory

TASK: [create dir2] *********************************************************** 
changed: [localhost]
tested by: 

PLAY RECAP ******************************************************************** 
*** Kirby Results ***
Coverage  : 50% (1 of 2 tasks are tested)
Not tested:
 - create dir2
*** Kirby End *******
localhost                  : ok=2    changed=2    unreachable=0    failed=0   
```

It tells us the coverage (50%) and the task not tested (create dir2).

## Installation

### Download

Make a `callback_plugins` directory in your playbook directory, and put `kirby.py` inside of it.

```
mkdir callback_plugins
cd callback_plugins
wget https://raw.githubusercontent.com/ks888/kirby/master/callback_plugins/kirby.py
```

### Setup

Make a `kirby.cfg` file in your playbook directory, and write the contents below.

```
[defaults]
enable = yes

serverspec_dir = ./
serverspec_cmd = bundle exec rake spec
```

* `serverspec_dir` is a directory to run serverspec.
* `serverspec_cmd` is a command to run serverspec.

## Usage

### Run

Run `ansible-playbook` command as usual.

* Hint: For the best results, your target system should be clean, that is, a playbook is not executed against the target system yet.

### Check Results

Results are like this:

```bash
~/src/kirby_demo% ansible-playbook create_2dirs.yml -i "localhost," -c local

PLAY [localhost] ************************************************************** 

TASK: [create dir1] *********************************************************** 
changed: [localhost]
tested by: 
- rspec ./spec/localhost/sample_spec.rb:4 # File "./dir1" should be directory

TASK: [create dir2] *********************************************************** 
changed: [localhost]
tested by: 

PLAY RECAP ******************************************************************** 
*** Kirby Results ***
Coverage  : 50% (1 of 2 tasks are tested)
Not tested:
 - create dir2
*** Kirby End *******
localhost                  : ok=2    changed=2    unreachable=0    failed=0   
```

* When a task's result is `changed`, Kirby determines whether the task is tested, and shows you the result(`tested by:`).
    * If the next line of `tested by:` is empty, the task was not tested (`create dir2` task is this).
    * If not empty, the task was tested (`create dir1` task is this).

* When a task's result is not `changed`, Kirby removes the task from the coverage, and shows nothing.

* At last, Kirby shows you a summary. It includes the coverage and the list of not tested tasks.

### Improve Coverage

If a task is not tested, let's write a serverspec test for the task.

However, you may think the test is not necessary for some tasks, such as:

* run `ls` using `command` module
* download a package in preparation for install.

There are 2 options for this:

1. use `changed_when`

    Kirby removes the task from the coverage when a task's result is not `changed`. So, if a `changed` task does not change the target system actually, use [changed_when](http://docs.ansible.com/ansible/playbooks_error_handling.html#overriding-the-changed-result) to control the result.

2. use `coverage_skip`

    Kirby removes the task from the coverage when a task's name includes `coverage_skip`. So, if you sure the test is not necessary, use it like this:

```bash
- name: create dir2 [coverage_skip]
  file: path=./dir2 state=directory
```

## FAQ

* [How does Kirby work?](https://github.com/ks888/kirby/blob/master/FAQ.md#work)
* [It takes longer time to run a playbook.](https://github.com/ks888/kirby/blob/master/FAQ.md#slow)
* [How can I disable Kirby?](https://github.com/ks888/kirby/blob/master/FAQ.md#disable)

## Contributing

Contributions are very welcome, including bug reports, idea sharing, feature requests, and English correction of documents. Feel free to open an issue or a pull request, or [contact me](https://twitter.com/ks888sk) on twitter.
