# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/fts.h

Declares compatibility FTS traversal APIs.

It exposes `fts_children`, `fts_close`, `fts_open`, `fts_read`, and `fts_set` using legacy `FTS`/`FTSENT` ABI declarations.

Filesystem relevance is direct through directory tree traversal.
