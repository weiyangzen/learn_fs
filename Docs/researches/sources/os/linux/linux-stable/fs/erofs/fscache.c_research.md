# File Research: sources/os/linux/linux-stable/fs/erofs/fscache.c

## Summary
Implements deprecated fscache-backed on-demand EROFS access and shared-domain cookie management.

## Main Responsibilities
- Reads data from fscache cookies into folios or bios.
- Handles inline data and holes for fscache-backed files.
- Registers fscache volumes and cookies.
- Supports shared domains across EROFS instances.
- Manages anonymous inodes for cached blobs.

## Key APIs
- `erofs_fscache_access_aops`
- `erofs_fscache_register_fs()`
- `erofs_fscache_unregister_fs()`
- `erofs_fscache_register_cookie()`
- `erofs_fscache_unregister_cookie()`

## Important Behavior
Data reads map logical ranges first, then choose inline copy, zero fill, or fscache read. Domain mode uses a pseudo mount and shared cookie list so blobs can be reused across mounts.

## Risks
This feature is explicitly deprecated in Kconfig. It has complex refcounting across requests, cookies, domains, pseudo inodes, and asynchronous fscache callbacks.
