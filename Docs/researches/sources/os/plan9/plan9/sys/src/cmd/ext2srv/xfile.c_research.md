# File Research: sources/os/plan9/plan9/sys/src/cmd/ext2srv/xfile.c

Manages open ext2 filesystem instances (`Xfs`) and per-fid state objects (`Xfile`).

Key behavior:
- `getxfs()` opens the device or default file, reuses an existing `Xfs` by qid/name, or allocates a new one and initializes ext2 via `ext2fs()`.
- `refxfs()` decrements references and, on last close, marks the superblock clean, syncs buffers, purges buffers, and closes the device fd.
- `xfile()` retrieves, allocates, cleans, or clunks `Xfile` state attached to lib9p fids.
- `clean()` releases the root's filesystem reference and resets per-fid state.

Important implementation details:
- Reuse is guarded by `xlock`; free `Xfile` reuse is guarded by `freelock`.
- `xfile(fid, Asis)` returns nil if the underlying `Xfs` has been closed.
- Only root fids hold `Xfs` references; cloned or walked fids share the attached root reference model.

Risks and invariants:
- `getxfs()` removes a failed new `Xfs` from the head list but does not free all partially allocated fields in every path.
- Filesystem cleanliness depends on the final root fid being clunked and `refxfs()` running.
