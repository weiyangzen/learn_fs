# File Research: sources/os/bsd/freebsd-src/sys/sys/unistd.h

Kernel/user visible POSIX option, pathconf, seek, rfork, and miscellaneous syscall constant header.

Key responsibilities:
- Defines implemented, unsupported, or runtime-determined POSIX option macros and target `_POSIX_VERSION`.
- Defines access mode constants, seek constants, BSD `SEEK_DATA`/`SEEK_HOLE`, and legacy `L_SET`/`L_INCR`/`L_XTND` aliases.
- Defines `_PC_*` pathconf names for POSIX and FreeBSD filesystem features including ACLs, capabilities, MAC, deallocation, named attributes/xattrs, hidden/system attributes, clone block size, case insensitivity, and minimum hole size.
- Defines BSD `rfork()` flags, signal-number packing helpers, valid/user/kernel-only flag masks, and process-descriptor/vfork/spawn semantics.
- Defines `kcmp()` selectors, swapoff force flag, `close_range()` flags, and `copy_file_range()` user-visible cloning flag.

Dependencies:
- Includes `sys/cdefs.h`.

Notable risks:
- Values that are zero require runtime `sysconf()` support capable of determining real availability.
- `RFPPWAIT` and `RFSPAWN` intentionally share the high bit in kernel/user interpretations, so context matters.
