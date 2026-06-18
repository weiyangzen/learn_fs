# File Research: sources/os/bsd/netbsd-src/sys/sys/times.h

Read completely: 65 lines.

Defines the POSIX `times(3)` process accounting ABI.

Key elements:
- Ensures `clock_t` is available from machine ANSI definitions.
- `struct tms` records user/system CPU time for the process and terminated children.
- Userland prototype declares `times(struct tms *)` with legacy symbol rename guard.

Risks and notes:
- `struct tms` is a stable user ABI.
- Clock tick interpretation depends on system configuration and `sysconf(_SC_CLK_TCK)`.
