# File Research: sources/local-fs/reiserfsprogs/include/reiserfs_lib.h

Public library API for reiserfsprogs. Defines `reiserfs_filsys_t`, in-memory bitmap state, hash function type, the filesystem handle, and transaction metadata.

The filesystem handle stores block size, format, hash function, device filenames/fds, superblock buffer, on-disk bitmap, journal device/header state, bad-block bitmap, dirty flags, private pointer, and block allocator/deallocator callbacks.

Declares APIs for opening/creating/flushing/closing filesystems, journal management, bitmap management, tree mutations, directory entry lookup/add/remove, key comparison/search, file and directory iteration, object-id tracking, bad-block list handling, node-format inspection, hash selection, stat-data field access, printing, and xattr/ACL validation.
