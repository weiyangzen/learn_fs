# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_select.c

Read completely: 102 lines.

This implements old `pollts`, `select`, and `pselect` with `timespec50`/`timeval50` timeout layouts. Each converts the optional timeout to native form and delegates to the corresponding `*50` wrapper.

Security/reliability notes: fd sets, pollfd arrays, and signal masks are forwarded unchanged. Null timeout pointers are supported.
