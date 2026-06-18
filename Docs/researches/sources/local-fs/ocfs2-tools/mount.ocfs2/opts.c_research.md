# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/opts.c

Mount option parser and canonical option-string builder for `mount.ocfs2`.

`parse_opts()` tokenizes comma-separated `-o` options, maps known options to `mount(2)` flags, stores unknown filesystem options in `extra_opts`, recognizes `nocluster`, and records string options like `loop=`, `vfs=`, `offset=`, `encryption=`, `speed=`, and `comment=`. It also converts nonnumeric `uid=` and `gid=` names to numeric IDs when possible.

`fix_opts_string()` reconstructs a normalized mtab option string from flags, preserved string options, extra filesystem options, and an optional user name. The parser intentionally hides selected helper-only options from the syscall or mtab via masks defined in `opts.h`.
