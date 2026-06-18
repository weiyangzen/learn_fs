# File Research: sources/virtualization/nbdkit/server/usergroup.c

This file implements `--user` and `--group` privilege dropping on platforms with password and group databases. `change_user` applies group first, then user. For groups it parses the configured group, calls `setgid`, then resets supplemental groups to just that gid with `setgroups`. For users it parses the configured user and calls `setuid`.

`parseuser` tries `getpwnam` first, then falls back to numeric parsing through `nbdkit_parse_int`. `parsegroup` mirrors this with `getgrnam`. On failure each prints a command-line specific diagnostic, includes saved lookup errno when available, and exits.

On platforms without `pwd.h` and `grp.h`, `change_user` is a no-op when neither option is set, otherwise reports that `--user/--group` are not implemented on Windows.
