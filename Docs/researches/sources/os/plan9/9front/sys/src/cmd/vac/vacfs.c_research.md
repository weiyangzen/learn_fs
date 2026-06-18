# File Research: sources/os/plan9/9front/sys/src/cmd/vac/vacfs.c

Purpose: Exposes a Vac archive as a 9P filesystem.

Key behavior:
- Starts as a mounted filesystem, `/srv` service, or stdio 9P server.
- Opens the requested Vac archive read-only and serves 9P requests from a Venti-backed `VacFs`.
- Maintains a linked list of `Fid` records with user, qid, open state, `VacFile`, and directory enumerator.
- Handles 9P version, attach, walk, open, read, clunk, remove, stat, and read-only errors for write/wstat.
- Converts `VacDir` to Plan 9 `Dir` records with qid offsets, qid-space metadata, append/exclusive/directory flags, sizes, owners, and times.
- Implements directory reads with `VacDirEnum`, preserving unread entries when a stat record will not fit.
- Enforces owner/group/other permission checks unless `-p` disables checks.

Dependencies:
- Uses `fcall.h`, Plan 9 mount/service APIs, Venti formats, and Vac file/directory APIs.

Notable details:
- Although some create/remove handlers exist, the archive is opened with `VtOREAD`; write-side operations return read-only errors in normal use.
- Supports both `9P2000` and `9P2000.u` stat conversion through local compatibility macros.
