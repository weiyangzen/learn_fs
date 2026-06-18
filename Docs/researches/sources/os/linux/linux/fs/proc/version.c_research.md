# File Research: sources/os/linux/linux/fs/proc/version.c

## Scope

This file implements `/proc/version`.

## Public And Internal APIs Covered

- Display callback: `version_proc_show()`.
- Init: `proc_version_init()`.

## Control Flow And Behavior

- `version_proc_show()` formats `linux_proc_banner` with system name, release, and version from `utsname()`.
- Init creates a permanent single-show proc entry named `version`.

## Dependencies And Risks

- Depends on UTS namespace/kernel version data and the global `linux_proc_banner` format.
- Userspace expects this legacy single-line version report to remain stable enough for diagnostics.
