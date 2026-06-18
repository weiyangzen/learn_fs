# File Research: sources/os/plan9/plan9/sys/src/cmd/mntgen.c

Implements `mntgen`, a synthetic 9P filesystem that dynamically creates empty directories when walked.

Behavior:
- Usage: `mntgen [-s srvname] [mtpt]`.
- Mounts a read-only directory service at `mtpt` or `/n`.
- Walking a non-existent name at root creates a new directory entry.
- Child directories are empty.
- Directories are removed from the table when the last fid referencing them is clunked.

Key structures:
- `Tab` stores name, qid path, creation time, and ref count.
- Qid paths are 48-bit MD5-derived hashes of names.

9P handlers:
- `fsattach`, `fsopen`, `fsread`, `fsstat`, `fswalk`, `fsclunk`.

Notes:
- Root qid path is `0`.
- Name hash collisions are rejected.
- Files are read-only; only directory reads/stat/walks are meaningful.
