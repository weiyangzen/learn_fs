# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/plan9.c

Plan 9 platform adapter for the 9660 tool.

`dirtoxdir` copies Plan 9 `Dir` metadata into `XDir`, atomizing name/user/group and preserving mode, atime, mtime, and length. Numeric uid/gid are set to zero. `fdtruncate` is a no-op on Plan 9.

Integration points: alternative to `unix.c` depending on build target.

Risks and notes: no truncation support in this adapter, and numeric uid/gid are not resolved.
