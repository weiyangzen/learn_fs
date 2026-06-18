# File Research: sources/os/bsd/netbsd-src/sys/sys/acct.h

Read completely: 88 lines.

Defines NetBSD process accounting record ABI.

Key elements:
- `comp_t` is a 16-bit compact floating-point accounting type with a 3-bit base-8 exponent and 13-bit fraction.
- `struct acct` records command name, user/system/elapsed time, start time, uid/gid, average memory, I/O block count, controlling tty, and flags.
- Accounting time fields use `AHZ` granularity, defined as 64 units per second.
- Flags include `AFORK`, `ASU`, `ACOMPAT`, `ACORE`, and `AXSIG`, with `__ACCT_FLAG_BITS` for bit decoding.
- Kernel prototypes expose `acct_init()` and `acct_process()`.

Risks and notes:
- `struct acct` is a binary accounting-file ABI; changing fields or layout would affect accounting consumers.
- Compact time/accounting fields are lossy by design.
