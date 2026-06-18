# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwalk.c

Read completely: 66 lines.

This file implements `_fwalk`, iterating every allocated `FILE` in the glue list and OR-ing the return value of a caller-supplied function for streams with nonzero flags.

Important interactions: used by `fflush(NULL)` and cleanup-style operations.

Security/reliability notes: caller is responsible for external locking when walking the global stream list.
