# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/fd2path.c

This test/helper command prints kernel paths for file descriptors.

Key behavior:
- Usage: `fd2path path ...`.
- With no args, prints `fd2path(0)`.
- With args, opens each path and prints the resolved path for the fd.

Integration and risks:
- Simple diagnostic for Plan 9 fd/path behavior.
