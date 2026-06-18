# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dir.c

## Scope

Directory-tree scanner and repair logic for `fsck_msdos`. It validates short and long filename entries, directory structure, file sizes versus cluster chains, directory start clusters, and reconnects lost chains into `LOST.DIR`.

## Main APIs

- `resetDosDirSection()` allocates directory scan state and initializes the root directory object.
- `finishDosDirSection()` frees directory tree, pending todo list, and buffers.
- `handleDirTree()` scans root and pending subdirectories.
- `reconnect()` creates an entry in `LOST.DIR` for a lost FAT chain.
- `finishlf()` frees lost-file reconnect buffer.

## Control Flow

The scanner maintains a lightweight in-memory tree of `dosDirEntry` nodes and a stack of pending directories. `readDosDirSection()` reads either the fixed FAT12/16 root area or cluster-chain directory data. It parses 32-byte entries, handles `SLOT_EMPTY` and deleted slots, optionally truncates entries after end-of-directory, reconstructs Win95 long filenames, validates LFN checksum/order/cluster fields, and removes invalid LFN ranges when approved.

For normal entries it builds an 8.3 name, applies any valid long name, decodes start cluster and size, removes invalid volume-label LFNs, drops clusters from zero-size files, validates start clusters, fixes directory sizes to zero, repairs `.` and `..` start clusters, queues subdirectories, and checks ordinary file size against chain length. Superfluous clusters can be dropped via `clearchain()`.

`reconnect()` locates `LOST.DIR`, finds a free slot, writes a numeric short-name entry for the lost chain head, and marks the FAT chain used.

## Dependencies

- FAT state from `struct fatEntry`: `next`, `head`, `length`, `FAT_USED`.
- Boot geometry from `struct bootblock`.
- FAT helpers `clearchain()`, `writefat()`, and `rsrvdcltype()`.
- Prompt/error helpers from `ext.h`/`fsutil`.

## Risks And Edge Cases

- Long filename handling degrades non-ASCII UTF-16 bytes to `?`; it does not do full Unicode conversion.
- Directory tree linking inserts a new child at `dir->child`, replacing the previous head in the local copy path; this old code relies mainly on traversal stack and limited tree usage.
- `LOST.DIR` is not created or extended; reconnect fails if it is absent or full.
- Comments note unimplemented uniqueness checks for reconnected names and several `XXX` areas.
