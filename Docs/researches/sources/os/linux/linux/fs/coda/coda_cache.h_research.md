# File Research: sources/os/linux/linux/fs/coda/coda_cache.h

Header for Coda minicache operations.

Declares:
- Permission cache APIs: `coda_cache_enter()`, `coda_cache_clear_inode()`, `coda_cache_clear_all()`, `coda_cache_check()`.
- Child invalidation API: `coda_flag_inode_children()`.

Role:
- Shared by Coda directory/cache/upcall paths that need permission caching or invalidation after Venus downcalls.
