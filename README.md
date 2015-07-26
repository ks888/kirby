# Kirby

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

Here is the [Serverspec](http://serverspec.org/) test. There is 1 test for the first playbook task (create dir1).

```bash
~/src/kirby_demo% cat spec/localhost/sample_spec.rb 
require 'spec_helper'

describe file('./dir1') do
  it { should be_directory }
end
```

Now, run the playbook. Kirby shows you the code coverage.

```bash
~/src/kirby_demo% ansible-playbook demo1.yml -i "localhost," -c local

PLAY [localhost] **************************************************************

TASK: [create dir1] ***********************************************************
changed: [localhost]

TASK: [create dir2] ***********************************************************
changed: [localhost]

PLAY RECAP ******************************************************************** 
*** Kirby Results ***
Coverage   : 50% (1 of 2 tasks are tested)
Not covered:
 - create dir2
*** Kirby End *******
localhost                  : ok=2    changed=2    unreachable=0    failed=0   
```

Since there is 2 tasks and only 1 task is tested, the coverage is 50%. See [How it works](#how-it-works) for details.

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
enable_kirby = yes

serverspec_dir = <directory to run serverspec>
serverspec_cmd = <command to run serverspec>
```

### Run

Run `ansible-playbook` command as usual.

<a name="how-it-works"/>
## How it works

TBA

## Contributing

Contributions are very welcome, including bug reports, idea sharing, feature requests, and English correction of documents. Feel free to open an issue or a pull request.
