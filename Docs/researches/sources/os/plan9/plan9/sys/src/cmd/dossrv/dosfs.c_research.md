# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.c

Implements the 9P request handlers for the DOS/FAT filesystem server.

Key behavior:
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- `rattach()` opens or reuses the backing filesystem, parses FAT metadata via `dosfs()`, and creates a synthetic root fid.
- `rwalk()` supports cloning, `.`/`..`, long/short name lookup, directory qid assignment, and FAT directory type bits.
- `ropen()` enforces read-only attributes, `ORCLOSE`, truncate, directory/write rules, and open mode flags.
- `rcreate()` creates short or long-name directory entries, allocates first cluster for new directories, and writes `.`/`..`.
- `rread()` and `rwrite()` dispatch to directory serialization or file byte I/O.
- `rremove()` validates parent permissions and empty directories, truncates cluster chains, and marks directory entries deleted.
- `rwstat()` supports mode/mtime changes, truncation, contiguous-file conversion through `DMAPPEND`, and rename by remove-and-recreate; moved directory-entry pointers are propagated to other open fids.

Filesystem relevance:
- This is the protocol-facing mutation layer translating Plan 9 9P calls into FAT directory and allocation operations.
