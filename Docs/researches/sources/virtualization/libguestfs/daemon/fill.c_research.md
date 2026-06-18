# File Research: sources/virtualization/libguestfs/daemon/fill.c

Provides file creation/filling helpers: `do_fill`, `do_fill_pattern`, and `do_fill_dir`.

Important behavior:
- `do_fill` validates byte value `0..255` and non-negative length, then writes BUFSIZ chunks to a chrooted file.
- `do_fill_pattern` requires a non-empty pattern and writes repeated pattern fragments until length is reached.
- `do_fill_dir` creates numbered files `%08d` in a target directory.
- Progress is reported during fill loops.

Filesystem relevance: stress/test utility for allocating data or many dentries inside the guest filesystem.
