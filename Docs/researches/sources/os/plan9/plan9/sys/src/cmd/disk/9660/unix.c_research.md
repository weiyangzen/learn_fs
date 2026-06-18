# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/unix.c

Unix platform adapter for the 9660 tool.

`dirtoxdir` copies `Dir` metadata into `XDir`, resolves textual user/group names to numeric uid/gid with `getpwnam`/`getgrnam`, preserves times/length/mode, and records symlink targets when the mode has `CHLINK`, forcing symlink permissions to `0777`.

`fdtruncate` calls POSIX `ftruncate`. `numericuid` and `numericgid` warn once if name lookup fails and return zero.

Integration points: alternative to `plan9.c` for Unix builds; provides numeric IDs used by Rock Ridge PX records.

Risks and notes: only the first lookup failure warning is printed per uid/gid resolver. Failed lookups silently become uid/gid 0 after warning.
