# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_sigaltstack.c

Read completely: 68 lines.

This implements old `sigaltstack` using `struct sigaltstack13`. It maps old stack fields into native `stack_t`, calls `__sigaltstack14`, then maps the old stack result back, clamping `ss_size` to `INT_MAX`.

Security/reliability notes: `onss` is dereferenced unconditionally, so it does not support a null new-stack pointer despite modern `sigaltstack` allowing query-only calls. Output size clamping avoids overflowing old `int` size.
