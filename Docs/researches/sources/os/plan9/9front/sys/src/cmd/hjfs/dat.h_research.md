# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/dat.h

Defines `hjfs` on-disk constants, block structures, runtime state, and flags.

Key points:
- On-disk constants:
  - `BLOCK = 4096`
  - `RBLOCK = BLOCK - 1` because the first byte stores block type
  - `SUPERMAGIC`
  - `SUPERBLK`
  - name length, direct/indirect block counts, root qids
- Runtime constants:
  - sync interval
  - freelist length
  - buffer hash size
  - worker count
  - exclusive lock duration
  - user name/id constants
- Block types:
  - `TRAW`
  - `TSUPERBLOCK`
  - `TDENTRY`
  - `TINDIR`
  - `TREF`
  - `TDONTCARE`
- Defines `Superblock`, `Dentry`, `BufReq`, `Buf`, `ThrData`, `Dev`, `FLoc`, `Loc`, `Fs`, and `Chan`.
- `Dentry` embeds Plan 9 `Qid`, ownership, mode, size, direct/indirect block pointers, and times.
- Reference counts are stored as 24-bit entries with sentinel value.
- `Loc` tracks in-memory file locations, reference state, dump flags, and exclusive locks.
- `Fs` carries device, flags, root location, freelist, location tree, and user database.
- `Chan` carries per-fid filesystem state, directory walk state, and queued worker requests.
- Defines `HOWMANY()` for block count rounding.

Dependencies and interactions:
- Included by all `hjfs` files.
- Matches serialization logic in `conv.c`.

Research relevance:
- Central structural definition of the `hjfs` filesystem’s disk format and runtime object model.
