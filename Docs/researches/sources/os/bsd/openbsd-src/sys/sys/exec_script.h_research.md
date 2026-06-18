# File Research: sources/os/bsd/openbsd-src/sys/sys/exec_script.h

This header defines script-exec recognition constants and the kernel script exec hook.

Key definitions:
- `EXEC_SCRIPT_MAGIC` as `#!`
- `EXEC_SCRIPT_MAGICLEN`
- `EXEC_SCRIPT_HDRSZ`, based on magic, separator, `MAXINTERP`, and terminator.

Kernel API:
- `exec_script_makecmds`

Risk notes:
- Header-size calculation depends on `MAXINTERP` from included exec context.
- Script handling interacts with `EXEC_INDIR`, fake argv, and held script file descriptors in `exec_package`.
