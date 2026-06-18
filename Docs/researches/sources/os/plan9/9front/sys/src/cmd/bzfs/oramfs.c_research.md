# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/oramfs.c

This is an in-memory 9P ramfs implementation used by `bzfs`.

Major responsibilities:
- Serves 9P requests over pipes/stdio.
- Maintains a fixed `Ram ram[Nram]` array of file metadata and content.
- Maintains dynamic fid list `Fid`.
- Implements core 9P handlers: version, attach, walk, open, create, read, write, clunk, remove, stat, wstat.
- Mounts itself at a requested mountpoint, publishes `/srv/ramfs`, or uses stdio mode for kernel/loader use.

Filesystem model:
- Root starts as `.` with `DMDIR | 0775`.
- File data is stored in heap buffers, capped by `Maxsize` sanity check.
- Directory reads synthesize stat records for children.
- Metadata uses Plan 9 `Dir`, `Qid`, `convD2M`, `convM2D`.

Notable implementation details:
- User/group strings are interned by `atom`; atoms are intentionally never freed.
- Permission checks exist but many are behind `#ifdef CHECKS`; ownership checks are behind `#ifdef OWNERS`.
- `DMAPPEND`, `DMEXCL`, `ORCLOSE`, truncation, qid versions, and wstat length changes are supported.
- Message size is negotiated by `Tversion`.

Risks and caveats:
- Fixed maximum of 512 `Ram` entries.
- Removal does not recursively check directory children.
- Many permission checks are compiled out by default.
- `rwalk` compares `rhdr.newfid`/`rhdr.fid`, but request fields conventionally live in `thdr`; this deserves scrutiny in maintenance.
