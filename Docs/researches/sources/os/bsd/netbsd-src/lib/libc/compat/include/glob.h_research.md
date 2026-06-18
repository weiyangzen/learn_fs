# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/glob.h

Declares compatibility globbing APIs.

It exposes old `glob` and `globfree` declarations using `glob_t`.

Filesystem relevance is direct: pathname expansion depends on directory traversal and stat-like filesystem behavior.
