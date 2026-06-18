# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/softdep.h

## Purpose

Defines the in-memory dependency records and state flags used by UFS/FFS soft updates. This header is structural rather than executable: it describes how metadata write ordering is represented for inode updates, block allocation, block freeing, directory additions/removals, mkdir/rmdir, and indirect-block updates.

## Key Definitions

- State flags: `ATTACHED`, `UNDONE`, `COMPLETE`, `DEPCOMPLETE`, `MKDIR_PARENT`, `MKDIR_BODY`, `RMDIR`, `DIRCHG`, `GOINGAWAY`, `IOSTARTED`, `ONWORKLIST`.
- `ALLCOMPLETE` means a dependency is attached, complete, and dependency-complete.
- `struct worklist` is the common first field for softdep work items. The file explicitly requires it to be first so cast macros such as `WK_INODEDEP()` and `WK_DIRADD()` are valid.
- Queue/list heads: `dirremhd`, `diraddhd`, `newblkhd`, `inodedephd`, `allocindirhd`, `allocdirecthd`, `allocdirectlst`.

## Main Structures

- `struct pagedep`: tracks dependencies for one directory page, including pending directory removals and directory additions hashed by offset.
- `struct inodedep`: tracks delayed inode work, inode-buffer wait lists, pending directory-name writes, and direct block allocation updates associated with an inode.
- `struct newblk`: represents an allocated block/fragment whose cylinder-group bitmap write may still be pending.
- `struct bmsafemap`: attaches allocation dependencies to a cylinder-group bitmap buffer.
- `struct allocdirect`: tracks a newly allocated direct block or fragment that cannot be claimed by the inode until data and bitmap dependencies complete.
- `struct indirdep` and `struct allocindir`: track safe copies and allocation dependencies for indirect block pointers.
- `struct freefrag`, `struct freeblks`, `struct freefile`: deferred block, fragment, and inode freeing records.
- `struct diradd`: tracks directory entries that cannot be written until referenced inode and mkdir dependencies are safe.
- `struct mkdir`: represents the two special mkdir dependencies: writing the new directory body and writing the parent inode link-count update.
- `struct dirrem`: represents a deferred link-count decrement after a directory entry removal reaches disk.

## Important Behavior Encoded By The Design

Soft updates uses rollback/roll-forward around buffer I/O. For example, unsafe pointers are temporarily undone before disk write, restored after I/O, and freed only when both local and upstream dependencies are complete. Directory operations are decomposed into separately ordered pieces so link counts, directory bodies, and names reach disk in crash-safe order.

## Dependencies And Integration Points

This header depends on queue/list primitives from `<sys/queue.h>` and on UFS/FFS types such as `struct fs`, `struct buf`, `struct vnode`, `ufs_daddr_t`, `ufs_lbn_t`, and inode/directory structures declared elsewhere. The functions that consume these structures are declared in `ufs_extern.h` and implemented in the softdep subsystem outside this file.

## Notes For Future Work

- The `worklist` first-field invariant is critical. Reordering fields in any softdep work item would break the cast macros.
- The header defines `mkdirlisthd` directly, which is a global list head declaration/definition in this old kernel style.
- Many fields intentionally overload state or union storage to keep structures small; changes must preserve those lifetime assumptions.
