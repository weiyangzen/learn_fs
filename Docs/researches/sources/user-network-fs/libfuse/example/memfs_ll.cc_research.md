# sources/user-network-fs/libfuse/example/memfs_ll.cc

## Purpose

`memfs_ll.cc` is a C++20 low-level libfuse in-memory filesystem example. It implements mutable files and directories with inode/dentry classes, lookup counts, hard links, rename, mkdir/rmdir/unlink, setattr, statfs, directory handles, and multi-threaded session looping. The source was read as a complete 1139-line file.

## Important APIs, Types, and Functions

Core types are `Inode`, `Dentry`, `Inodes`, and `DirHandle`. Low-level callbacks in `memfs_oper` include `memfs_lookup`, `memfs_forget`, `memfs_forget_multi`, `memfs_getattr`, `memfs_setattr`, `memfs_mkdir`, `memfs_unlink`, `memfs_rmdir`, `memfs_rename`, `memfs_link`, `memfs_open`, `memfs_read`, `memfs_write`, `memfs_release`, `memfs_opendir`, `memfs_readdir`, `memfs_releasedir`, `memfs_statfs`, and `memfs_create`.

## Control Flow

The global `Inodes` table starts with root. Create/mkdir allocate an inode, create a dentry, attach it to the parent, and reply with entry data. Lookup finds a child dentry and increments lookup count. Read/write operate on `Inode::content`. Opendir snapshots children into a `DirHandle`; readdir serializes that snapshot. Forget decrements lookup count and erases inodes when it reaches zero. Rename locks global and parent directories, removes existing targets as needed, and moves by creating a new dentry for the same inode.

## State and Persistence Behavior

All filesystem data is memory resident in the global inode table, inode content vectors, dentry vectors, attributes, link counts, and lookup counts. There is no disk persistence. Attribute and entry timeouts are zero, forcing fresh kernel queries.

## Dependencies and Integration Points

It depends on C++ STL containers/locks/atomics and `fuse_lowlevel.h`. Meson builds it when C++ is available on non-DragonFly platforms.

## Risks and Edge Cases

Locking is complex and not fully consistent: some methods use inode mutexes, some attr mutexes, and some call `Inodes.find` while holding `Inodes.lock`. `memfs_link` stores a raw dentry pointer from a `unique_ptr` that is destroyed at function exit, causing a dangling directory entry. `memfs_mkdir` cleanup calls `erase_locked` without visibly holding the global lock on that path. `memfs_forget_multi` decrements lookup counts but does not erase zero-count inodes. Removal decrements nlink but does not erase unreferenced content by link count.

## Test Signals

High-value tests are fsx-style create/write/read/truncate/unlink, mkdir/rmdir non-empty, hard link lifetime, rename overwrite and cross-directory rename, lookup/forget accounting, readdir snapshot behavior, chmod/chown/utimens/truncate through setattr, multi-thread stress, and sanitizer runs for dangling dentry/use-after-free.
