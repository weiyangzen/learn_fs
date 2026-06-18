# File Research: sources/os/bsd/dragonflybsd/sys/sys/acct.h

Read completely: 85 lines.

This header defines process accounting record formats.

Key contents:
- `comp_t`, a compact 3-bit exponent/13-bit fraction time/accounting type.
- `struct acct` with command name, user/system/elapsed time, start time, uid/gid, memory, I/O count, controlling tty, and accounting flags.
- Flags for fork-without-exec, superuser use, compatibility mode, core dump, and signal death.
- Accounting tick granularity `AHZ`.
- Kernel prototype `acct_process(struct proc *)`.

Security/reliability notes:
- No runtime logic here. The structure is on-disk/user-visible accounting ABI, so field widths and `AC_COMM_LEN` matter.
