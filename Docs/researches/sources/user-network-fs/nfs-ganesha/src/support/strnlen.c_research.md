# sources/user-network-fs/nfs-ganesha/src/support/strnlen.c

Purpose: compatibility implementation for bounded string length when the platform lacks `HAVE_STRNLEN`.

Important APIs, types, and functions: exports `size_t gsh_strnlen(const char *s, size_t max)`. The name is project-specific rather than overriding libc `strnlen`.

Control flow: iterates from `s` until NUL or until `max` characters have been consumed, then returns pointer distance.

State and persistence: no persistent state.

Dependencies and integration points: depends on `<sys/types.h>` and `<stdlib.h>`. Other code can use `gsh_strnlen` as a portable bounded string helper.

Risks: input must point to readable memory for at least `max` bytes or contain a prior NUL. The post-decrement loop is correct but easy to misread.

Test signals: tests should cover zero max, shorter-than-max strings, no-NUL-within-max buffers, and empty strings.
