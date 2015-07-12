# Kirby

Code Coverage Tool for Ansible

## Description

It is usual to measure the code coverage for your source code written in python, Java, and so on. However, it is very few to measure it for your Ansible playbook. Kirby is the tool to support this.

Here is the example to measure the code coverage. [Serverspec](http://serverspec.org/) is used as the testing tool.

```bash
~/src/kirby_demo% cat demo1.yml
---
- hosts: localhost
  gather_facts: no
  tasks:
    - name: create dir1
      file: path=./dir1 state=directory

    - name: create dir2
      file: path=./dir2 state=directory

~/src/kirby_demo% cat spec/localhost/sample_spec.rb 
require 'spec_helper'

describe file('./dir1') do
  it { should be_directory }
end

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

~/src/kirby_demo% 
```

Serverspec runs whenever a task results in *changed* status. If the number of failed tests in serverspec is smaller than the last run, the task is regarded as *tested*. In this example, 1st task is *tested*, but 2nd task is not, so the test coverage is 50%.

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

serverspec_dir = ./
serverspec_cmd = bundle exec rake spec
```

`serverspec_cmd` is the command to run serverspec, and `serverspec_dir` is the directory to run it.

### Run

Run `ansible-playbook` command as usual.

* To measure the code coverage correctly, your target host should be clean, that is, Ansible is yet to setup the target host.

<a name="how-it-works"/>
## How it works

TBA

## Contributing

Contributions are very welcome, including bug reports, idea sharing, feature requests, and English correction of documents. Feel free to open an issue or a pull request.
