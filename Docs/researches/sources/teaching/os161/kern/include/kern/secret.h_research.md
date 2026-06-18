# File Research: sources/teaching/os161/kern/include/kern/secret.h

Automated-testing secret header.

Key contents:
- Warns not to modify; contents are overwritten during automated testing.
- Undefines `SECRET_TESTING`.
- Defines placeholder `SECRET "SECRET"`.

Relevance:
- Included by `kern/test161.h` to gate test progress and scoring helpers.
