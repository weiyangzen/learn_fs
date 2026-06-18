# File Research: sources/os/bsd/openbsd-src/sbin/init/pathnames.h

This header supplies init-specific path definitions.

Key contents:
- Includes `<paths.h>` for standard system paths such as `_PATH_DEV`, `_PATH_DEVNULL`, `_PATH_CONSOLE`, `_PATH_BSHELL`, and `_PATH_STDPATH`.
- Defines `_PATH_RUNCOM` as `/etc/rc`.

Usage:
- `init.c` uses `_PATH_RUNCOM` for boot and shutdown script execution.
- Other standard paths from `<paths.h>` drive console, shell, device, and stdpath behavior.

Security and correctness notes:
- Centralizing `/etc/rc` here keeps boot/shutdown script path consistent across `init.c`.
