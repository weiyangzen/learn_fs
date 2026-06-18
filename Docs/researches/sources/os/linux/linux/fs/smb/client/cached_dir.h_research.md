# File Research: sources/os/linux/linux/fs/smb/client/cached_dir.h

Declares CIFS cached directory data structures and public cache APIs.

`cached_dirent` stores a cached readdir entry name, position, and file attributes. `cached_dirents` tracks per-open-file dirent cache validity, failure, expected position, mutex, list, and accounting.

`cached_fid` represents a cached directory handle, including path, lease/open/list/file-info validity flags, timestamps, refcount, SMB fid, tcon, dentry, async work items, dirent cache, and embedded `smb2_file_all_info`.

`cached_fids` is the per-tcon cache container with a spinlock, active and dying lists, delayed laundromat work, and aggregate counters. The exported API opens, finds, closes, drops, invalidates, and lease-breaks cached directories.
