# sources/distributed-fs/xrootd/src/XrdOss/XrdOssUnlink.cc

Purpose: implements OSS removal operations for files, directories, symlinks, and optional remote/MSS copies, including cache usage adjustment.

Important APIs/types/functions: `XrdOssSys::Remdir`, `XrdOssSys::Unlink`, and private `BreakLink`.

Control flow: `Remdir()` translates to a local path unless already a PFN, verifies the target is a directory, and delegates to `Unlink()`. `Unlink()` builds local and remote paths, enforces read-only checks for LFNs, handles ENOENT as success locally, breaks symlinks by deleting their target, removes directories with `rmdir`, unlinks files, adjusts cache usage by device or cache-group path, and then, when permitted, removes the remote copy with `MSS_Unlink`.

State and persistence behavior: deletes filesystem namespace entries and can delete remote mass-storage entries. It updates in-memory/cache usage through `XrdOssCache::Adjust`. Symlink handling can remove both the link target and usage for the backing cache object.

Dependencies: `XrdOssApi`, `XrdOssCache`, `XrdOssConfig`, `XrdOssOpaque`, `XrdOssPath`, `XrdOssTrace`, POSIX `lstat`, `stat`, `readlink`, `unlink`, `rmdir`, and global `OssEroute`/`OssTrace`.

Integration points: backs client remove/rmdir operations and cleanup paths. It cooperates with path export flags, name translation, cache layout conventions, and remote-storage commands.

Risks: `BreakLink()` trusts symlink contents enough to unlink the target; path buffers are fixed-size; remote deletion after local ENOENT can remove offline data unless `XRDOSS_Online` is set; cache accounting depends on stat size and cache layout suffix detection; `Check_RO` result is stored as `remotefs`, making option semantics subtle.

Test signals: remove file, directory, symlink target, missing local file, remote-only file, online-only removal, read-only export rejection, cache adjustment for old/new cache layouts, and remote `MSS_Unlink` ENOENT handling.
