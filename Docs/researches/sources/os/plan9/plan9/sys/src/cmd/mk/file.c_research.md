# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/file.c

Handles file and archive modification times for `mk`.

Key functions:
- `mtime(name)` delegates to `mkmtime(name, 1)`.
- `timeof(name, force)` handles archive member targets, cache lookup, and forced stat.
- `touch(name)` updates file/archive time unless `nflag` is set.
- `delete(name)` removes regular files and refuses archive members.
- `timeinit(s)` implements `mk -w` by assigning current time to listed targets.

Dependencies:
- Archive helpers `atimeof` and `atouch`.
- Plan 9-specific `mkmtime` and `chgtime` from `plan9.c`.
