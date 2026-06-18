# File Research: sources/os/bsd/freebsd-src/sys/sys/acct.h

Process accounting record layouts.

Key elements:
- Defines `AC_COMM_LEN`.
- Defines current `struct acctv3`, older `struct acctv2`, and legacy `struct acctv1`.
- Defines accounting flags such as `AFORK`, `ACOMPAT`, `ACORE`, `AXSIG`, and `ANVER`.
- Defines legacy `comp_t` and `AHZV1`.
- Under `_KERNEL`, declares `acct_process()`.

Dependencies:
- Userland includes `sys/types.h`; kernel temporarily maps `float` to `uint32_t` for encoded accounting fields.

Research notes:
- Accounting records include command, CPU time, elapsed time, start time, uid/gid, memory, I/O block count, tty, and flags.
- Filesystem relevance comes from persistent accounting logs and encoded I/O counts.
