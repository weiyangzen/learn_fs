# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfile.c

Lifecycle manager for `dossrv` backing filesystems and 9P fids.

Key behavior:
- `getxfs()` opens the backing device/file, supports optional `name:sector-offset`, falls back to read-only when write-open fails, and reuses existing live `Xfs` instances by qid/name/offset after `devcheck()`.
- `refxfs()` reference-counts `Xfs`; when it reaches zero, it frees parsed FAT state, purges cached tracks, closes the device, and invalidates the fd.
- `xfile()` manages fid hash buckets, allocates/reuses `Xfile` structures, handles clunk, and refuses stale backing files.
- `clean()` drops a fid’s `Dosptr`, decrements its `Xfs`, and resets state.
- `dosptrreloc()` updates all open fids pointing at a directory entry that moved during rename.

Filesystem relevance:
- Bridges 9P fid lifetime to backing FAT-device lifetime and keeps open handles coherent across directory-entry relocation.
