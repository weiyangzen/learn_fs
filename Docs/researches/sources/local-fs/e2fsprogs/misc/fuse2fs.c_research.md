# File Research: sources/local-fs/e2fsprogs/misc/fuse2fs.c

## Purpose
Implements `fuse2fs`, a FUSE server that mounts ext2/ext3/ext4 filesystems through libext2fs.

## Key Elements
Defines the main `struct fuse2fs` context, per-open file handles, operation state, debug/log/timing helpers, timestamp encoding/decoding helpers, and a global mutex around libext2fs operations. Opens block devices/images with exclusive locking/retry behavior, optional lockfile, regular-file flocking, cache sizing, journal replay or `norecovery` handling, support checks, MMP background updates, and clean unmount bookkeeping.

Implements FUSE operations for init/destroy, getattr/readlink, mknod/mkdir/create, unlink/rmdir, symlink, rename, hard link, chmod/chown, truncate, open/read/write/release/fsync/statfs, xattrs, readdir, access, utimens, bmap, ioctls, FITRIM, shutdown, and fallocate where supported. Namespace operations use libext2fs allocation/link/unlink APIs and update ctime/mtime/atime, link counts, generation numbers, extra inode size, directory checksums, default ACL propagation, and optional dirsync flushing.

Option parsing handles `ro/rw`, `fakeroot`, debug, `norecovery/noload`, offset, OOM score, kernel-like mount behavior, direct I/O, ACLs, lockfile, timing, cache size, dirsync, and errors behavior. It computes default libfuse args including subtype/fsname/cache options and limits threads because libext2fs work is serialized.

## Dependencies
Depends heavily on libfuse, libext2fs internals, e2p, uuid, com_err, pthreads, e2fsprogs bthread/thread helpers, Linux filesystem ioctls/xattrs/fallocate/FITRIM where available, and optional NLS.

## Behavior/Risks
Rejects unsupported ext4 features including quota, verity, encryption, and casefolding. Shared-block filesystems and bigalloc with cluster ratio greater than one force read-only mode. Write mode warns that fuse2fs does not use the journal, so ungraceful unmount can cause corruption or data loss.

Error translation maps libext2fs failures to errno values, records first/last error data in the superblock, marks the filesystem erroneous, flushes metadata, and follows `errors=continue|remount-ro|panic`. Permission enforcement is partly internal unless `kernel` mode delegates to FUSE/kernel default permissions; group membership handling is best-effort. The file is large and stateful, with many operations relying on careful lock, inode, bitmap, and flush ordering.
