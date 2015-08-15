# FAQ

<a name="work"/>
## How does Kirby work?

Here are 3 points to understand Kirby.

1. After each task execution, Kirby runs serverspec.

    When Kirby is not installed, ansible works like this:

    ![before kirby](http://i.imgur.com/2AbjMfv.jpg)

    When Kirby is installed, ansible and Kirby work like this:

    ![after kirby](http://i.imgur.com/QXcgdwA.jpg)

    Note that, when the task's result is not `changed`, Kirby does not run serverspec, since its result should be same.

2. Determines whether a task is tested, by comparing serverspec's results.

    When serverspec runs, it returns a result like this:

    ```bash
    Failures:

      1) File "./dir1" should be directory
         Failure/Error: it { should be_directory }
           expected `File "./dir1".directory?` to return true, got false
         # ./spec/localhost/sample_spec.rb:4:in `block (2 levels) in <top (required)>'

    Finished in 0.79599 seconds (files took 0.79919 seconds to load)
    1 example, 1 failure

    Failed examples:

    rspec ./spec/localhost/sample_spec.rb:4 # File "./dir1" should be directory
    ```

    Kirby checks the number of failed tests (1 in this case).

    If the number of failed tests is smaller than the last one, the task is tested. Otherwise, not tested.

3. Calculate coverage

    `the number of tested tasks` / `the number of tasks`

     If Kirby removes tasks from the coverage, these tasks are not considered.

<a name="slow"/>
## It takes longer time to run a playbook.

It takes longer time, since Kirby runs serverspec many times.

Here are several ways to shorten running time:

1. Use `changed_when`

    Kirby does not run serverspec if the task's result is not `changed`, so use [changed_when](http://docs.ansible.com/ansible/playbooks_error_handling.html#overriding-the-changed-result) to override the task's result if possible.

2. Parallelize Serverspec

    It is easier than it sounds. There are useful gems like [parallel_tests](https://github.com/grosser/parallel_tests).

    [Here](http://mizzy.org/blog/2013/06/22/1/) is the blog post by the serverspec's author about it (it's Japanese, but Google translate works well).

[Please share your idea](https://twitter.com/ks888sk) to improve this!

<a name="disable"/>
## How can I disable Kirby?

To disable:

`export KIRBY_ENABLE=no`

To enable:

`export KIRBY_ENABLE=yes` or unset `KIRBY_ENABLE`.
