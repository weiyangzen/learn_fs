# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/sys.h

This header declares system-facing mail helper types, globals, and functions implemented mainly in `libsys.c` and `config.c`.

Key contents:
- Includes Plan 9 base, libc, and Bio headers.
- Defines `Mlock`, the lock-file handle containing fd, keeper pid, and lock name.
- Declares configurable global paths such as `MAILROOT`, `SPOOL`, `UPASLOG`, `UPASLIB`, `UPASBIN`, `UPASTMP`, `SHELL`.
- Declares file, lock, namespace, terminal, user, and mailbox creation helpers.
- Defines `Mboxmode = 0622`.

Integration and risks:
- Consumed by `common.h`; broad visibility makes these globals de facto configuration ABI for upas tools.
