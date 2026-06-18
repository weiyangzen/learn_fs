# File Research: sources/os/bsd/openbsd-src/sys/sys/acct.h

Purpose: Defines process accounting records and accounting flags.

Key contents:
- `comp_t` is a compact 16-bit accounting time/IO representation with base-8 exponent and fraction.
- `struct acct` records command name, user/system/elapsed time, IO blocks, start time, uid/gid, average memory, controlling tty, pid, and accounting flags.
- Flags identify fork-without-exec, syscall/stack mapping kill, core dump, signal kill, pledge violation, memory access violation, unveil violation, syscall pin violation, and BT CFI violation.
- `AHZ` defines accounting time granularity as 64 units per second.
- Kernel prototypes expose `acct_process()` and `acct_shutdown()`.

Filesystem relevance:
- Accounting can record filesystem-relevant termination causes such as pledge and unveil violations.
- Process accounting output itself is written through filesystem paths managed elsewhere.
