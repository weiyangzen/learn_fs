# File Research: sources/os/linux/linux-stable/fs/proc/version.c

Implements `/proc/version`.

Key points:
- Formats `linux_proc_banner` with system name, release, and version from `utsname()`.
- Registers `version` as a permanent single proc file.

Dependencies/contracts:
- Stable text ABI for kernel version reporting.
