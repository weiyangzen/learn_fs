# File Research: sources/os/plan9/plan9/sys/src/cmd/ramfs.c

Standalone in-memory 9P file server.

Data model:
- Fixed `ram[Nram]` array stores file/directory nodes.
- Linked `Fid` table maps 9P fids to `Ram` nodes.
- Root directory is initialized as `.` owned by the current user.
- File data is held in heap buffers, optionally capped by `Maxsize`.

Server behavior:
- `main()` supports stdio mode, service posting, mount point selection, private/noswap mode, debug logging, and unlimited-memory mode.
- `io()` reads 9P messages with `read9pmsg()`, dispatches through `fcalls`, and writes replies.
- Implements 9P operations: version, auth, flush, attach, walk, open, create, read, write, clunk, remove, stat, wstat.
- Directory reads serialize child `Dir` records with `convD2M()`.
- File reads return slices of stored data; writes grow buffers, zero gaps, update qid versions and mtimes.
- `rwstat()` supports rename, mode/group changes, and truncation/extension with simplified Plan 9 ownership/group rules.
- `perm()` checks owner/group/other bits based on the attached user.

Risk/notes:
- This is explicitly a toy-style filesystem; group membership assumes each user leads their own group.
- Fids and nodes are managed manually; user strings leak intentionally/minimally.
- Fixed node table can exhaust at 4096 busy entries.
- Remove-on-clunk (`ORCLOSE`) is implemented through `rclose`.
