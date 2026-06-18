# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/util.c

Provides small utility helpers for `hgfs`.

Key points:
- `hashstr()` implements a simple rolling hash for string hash tables.
- `getworkdir()` locates a Mercurial working directory:
  - uses an explicit path if supplied
  - otherwise starts at current directory and walks upward until `.hg` exists
- `readfile()` reads up to `nbuf - 1` bytes from a file and NUL-terminates the buffer, returning bytes read.

Dependencies and interactions:
- Used by `fs.c`, `hgdb.c`, `tree.c`, and `hash.c`.

Research relevance:
- Shared filesystem/path utility layer for locating Mercurial repositories and reading small metadata files.
