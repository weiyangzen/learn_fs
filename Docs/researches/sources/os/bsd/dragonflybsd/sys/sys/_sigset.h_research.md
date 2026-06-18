# File Research: sources/os/bsd/dragonflybsd/sys/sys/_sigset.h

Read completely: 41 lines.

This header defines the internal signal-set storage type.

Key contents:
- `_SIG_WORDS` is 4.
- `struct __sigset` contains four unsigned integer words.

Security/reliability notes:
- No runtime logic. The fixed storage size is ABI-sensitive for signal masks and contexts.
