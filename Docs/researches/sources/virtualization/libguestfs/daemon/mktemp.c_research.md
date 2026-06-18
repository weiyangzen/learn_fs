# File Research: sources/virtualization/libguestfs/daemon/mktemp.c

Temporary file and directory creation wrappers.

Important behavior:
- `do_mkdtemp` duplicates the template and calls `mkdtemp` under chroot.
- `do_mktemp` optionally appends a suffix, requiring the original template to end in `X`.
- Uses `mkstemps` under chroot and closes the created fd.
- Returns the generated guest path string.

Filesystem relevance: safe unique-name creation in guest filesystems.
