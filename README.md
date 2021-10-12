# Find stuck submissions in an A+ course instance

This is a small tool that finds "stuck" submissions in an
[A+ learning management system](https://github.com/apluslms)
course instance.
In the ideal world, such stuck submissions would not exist,
or this functionality would be provided in the A+ system directly.
But currently that is not the case, hence this tool.
To use the tool, you should have assistant or teacher role in the A+ course instance in question.

Before running
```shell
python3 find_stuck_submissions.py
```
edit the `find_stuck_submissions.yml` file as follows.
* The field `api-url` gives the API URL of the A+ installation in question. For instance, at Aalto University it is https://plus.cs.aalto.fi/api/v2/. Remember to include the trailing `/`.
* The field `course-id` is the integer identifier of the course instance you wish to scan for stuck submissions. One can find the course instances in the A+ API. For instance, the Aalto installation has them listed at https://plus.cs.aalto.fi/api/v2/courses/.
* The field `access-token` is your personal API access token (a sequence of characters and numbers) in the A+ installation. You can find it in your A+ profile information.
**Warning:** as the access token grants *your* rights to the course instance,
you should keep the `find_stuck_submissions.yml` file so that nobody else can access it by accident (set appropriate file premissions, do not commit it to a shared repository, and so on).
