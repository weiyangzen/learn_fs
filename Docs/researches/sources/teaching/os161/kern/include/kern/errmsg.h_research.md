# File Research: sources/teaching/os161/kern/include/kern/errmsg.h

Defines the error string table corresponding to `<kern/errno.h>`.

Key contents:
- `sys_errlist[]` maps error numbers to strings.
- `sys_nerr` records entry count.
- Must be included by exactly one implementation file because it defines storage.

Relevance:
- `strerror` uses this table; SFS and semfs print mount/getroot errors with `strerror(result)`.
