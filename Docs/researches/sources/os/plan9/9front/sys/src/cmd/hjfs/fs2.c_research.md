# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fs2.c

Implements the channel-level `hjfs` file API over the lower-level block and dentry primitives in `fs1.c`.

Key points:
- `chanattach` and `chanclone` create file channels rooted at either the live root or dump root.
- `chanwalk` validates directory traversal permissions, handles `.`, `..`, and named entries, and updates `Loc` references.
- `namevalid` rejects empty names, `.`/`..`, slash, control characters, and overlong names.
- `chancreat` validates permissions and read-only flags, allocates a new directory entry, assigns a qid, initializes the new dentry, inherits parent group, and opens the created object as requested.
- `chanopen` enforces read-only/permission/open-mode rules, handles append and truncate semantics, and implements Plan 9 exclusive-file locking with timeout.
- `chanread` reads regular files by block, returns zero-filled holes, and delegates directory reads to `chandirread`.
- `chanwrite` performs copy-on-write/overwrite-aware block writes, honors append mode, updates file size, and marks metadata modified.
- `statbuf`, `chanstat`, and `chandirread` serialize dentries into Plan 9 `Dir` structures for stat and directory reads.
- `chanclunk` releases channels, handles `ORCLOSE` removal, delays deletion for referenced entries, clears exclusive locks, and releases location chains.
- `chanwstat` implements rename, length changes, owner/group changes, mode changes, permission checks, and parent timestamp updates.
- `chanremove` is implemented by setting `CHRCLOSE` and clunking.

Dependencies and interactions:
- Depends on `fs1.c` functions such as `getdent`, `findentry`, `newentry`, `getblk`, `trunc`, `modified`, `delete`, `getloc`, and `putloc`.
- Uses user/group helpers such as `uid2name`, `name2uid`, `ingroup`, and `permcheck`.
- Works under `chbegin`/`chend` read locks unless channel flags suppress locking.

Research relevance:
- This file is the user-visible filesystem operation layer for `hjfs`, mapping Plan 9 file semantics onto the dentry/block implementation.
