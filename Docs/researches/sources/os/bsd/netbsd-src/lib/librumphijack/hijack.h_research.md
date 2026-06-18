# File Research: sources/os/bsd/netbsd-src/lib/librumphijack/hijack.h

Read completely: 28 lines.

## Purpose
Declares the private `rumphijack_dlsym()` helper used by the hijack library.

## Main Responsibilities
- Carries the local copyright/license block.
- Exposes one function prototype: `void *rumphijack_dlsym(void *, const char *);`.

## Filesystem Relevance
Indirect. It supports the dynamic-symbol resolution machinery used by `hijack.c`, which is filesystem-relevant through rump VFS syscall routing.

## Dependencies
None beyond normal C declaration context.
