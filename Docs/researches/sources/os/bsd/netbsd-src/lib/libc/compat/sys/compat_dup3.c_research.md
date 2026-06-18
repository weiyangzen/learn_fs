# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_dup3.c

Read completely: 76 lines.

This implements compatibility `dup3`. For distinct descriptors it delegates to `__dup3100`; for `oldfd == newfd`, it emulates allowed flag effects by updating file status flags with `F_GETFL`/`F_SETFL` and descriptor flags with `F_SETFD`.

Important interactions: supports compatibility behavior for same-fd `dup3`, including `O_NONBLOCK`, `O_NOSIGPIPE`, `O_CLOEXEC`, and `O_CLOFORK`.

Security/reliability notes: only the listed flags are handled in the same-fd path; unsupported bits are effectively ignored except through the masked cases. Errors from `fcntl` propagate.
