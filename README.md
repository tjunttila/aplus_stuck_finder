# Find stuck submissions in an A+ course instance

This is a small tool that finds "stuck" submissions in an
[A+ learning management system](https://github.com/apluslms)
course instance.
In the ideal world, such stuck submissions should not exist,
or this functionality should be provided in the A+ system directly.
But currently that is not the case, hence this tool.

Before running `python3 find_stuck_submissions.py`,
edit the `config.yaml` file as follows.
* The field `api-url` gives the API URL of the A+ installation in question. For instance, at Aalto University it is https://plus.cs.aalto.fi/api/v2/. Remember to include the trailing `/`.
* The field `course-id` is the integer identifier of the course instance you wish to scan for stuck instance. One can find the course instances in the A+ API. For instance, the Aalto installation has them listed at https://plus.cs.aalto.fi/api/v2/courses/
* The field `access-token` is your personal access token (a sequence of characters and numbers) in the A+ installation. You can find it in your "Account".
