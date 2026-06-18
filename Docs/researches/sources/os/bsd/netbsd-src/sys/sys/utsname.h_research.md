# File Research: sources/os/bsd/netbsd-src/sys/sys/utsname.h

Read completely: 62 lines.

Defines `uname(3)` system identity ABI.

Key elements:
- `_SYS_NMLN` is fixed at 256, with `SYS_NMLN` exposed under NetBSD source mode.
- `struct utsname` contains sysname, nodename, release, version, and machine strings.
- Declares `uname(struct utsname *)`.

Risks and notes:
- Fixed string sizes are public ABI.
- Values are populated elsewhere from kernel/system identity state.
