# File Research: sources/os/linux/linux-stable/fs/nfsd/filecache.h

## Summary
Header for NFSD file-cache objects and APIs.

## Contents
Defines `NFSD_FILE_GC_BATCH`, `struct nfsd_file_mark`, and `struct nfsd_file`. Declares file-cache lifecycle, acquire, put, lookup, close, disposal, and stats functions.

## Important Details
`struct nfsd_file` carries rhlist linkage, inode key, backing `struct file`, credential, net namespace, state flags, refcount, access mask, fsnotify mark, LRU/GC links, RCU head, birth time, and direct-I/O alignment attributes. File flags include `HASHED`, `PENDING`, `REFERENCED`, `GC`, and `RECENT`.

## Risks
`nf_inode` is not an owning pointer. `nfsd_file_mark` has an extra NFSD-specific refcount because fsnotify’s own mark refcount cannot express whether to destroy or only put the mark.
