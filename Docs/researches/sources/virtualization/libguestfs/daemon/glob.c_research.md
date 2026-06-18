# File Research: sources/virtualization/libguestfs/daemon/glob.c

Implements glob expansion inside the guest root.

Important behavior:
- Uses glibc `glob()` under `CHROOT_IN`.
- Defaults to `GLOB_BRACE | GLOB_MARK`.
- Optional `directoryslash=false` removes `GLOB_MARK`.
- `GLOB_NOMATCH` returns an empty list, not an error.
- Returns `glob_t.gl_pathv` directly and relies on caller-side freeing.

Filesystem relevance: expands guest path patterns while keeping lookup scoped through the daemon chroot mechanism.
