# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_core.c

Read completely: 360 lines.

Implements the loadable coredump module hook wiring and the generic coredump file creation/write path. `coredump_modcmd()` installs or removes hooks for the core writer, I/O helpers, NetBSD/ELF coredump formats, and UVM coredump map walkers.

`coredump()` enforces the core-size rlimit check, holds process credentials, blocks set-id coredumps unless explicitly configured, resolves the core filename pattern, checks `MNT_NOCOREDUMP` on the containing filesystem, opens the target with `O_CREAT | O_NOFOLLOW | FWRITE`, rejects non-regular files, multiply linked files, and files not owned by the dumping effective UID, truncates the target, optionally applies configured set-id core owner/group/mode, and calls the process execsw coredump routine. `coredump_write()` writes through `vn_rdwr()` with `IO_NODELOCKED | IO_UNIT` and advances the output offset; `coredump_offset()` returns the current offset.

`coredump_buildname()` expands `%n` process command, `%p` PID, `%u` session login name, and `%t` process start time into the configured pattern while enforcing `MAXPATHLEN`.

Risks and notes: the in-source comment says the data+stack+USPACE rlimit check is wrong for mapped data. Directory validation for complex paths uses an acknowledged double-lookup pattern. The return value from `VOP_SETATTR()` during truncation/metadata setup is not checked. Core files are opened no-follow and must have link count one, which reduces symlink/hardlink leakage risk.
