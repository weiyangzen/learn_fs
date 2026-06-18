# File Research: sources/os/linux/linux-stable/fs/cachefiles/security.c

This file manages credentials and LSM security context for CacheFiles backing filesystem access.

Main functions:
- `cachefiles_get_security_ID()` creates kernel credentials from `current`. If the daemon configured a security context with `secctx`, it applies that secid using `set_security_override()`. The resulting credentials are stored in `cache->cache_cred`.
- `cachefiles_determine_cache_security()` replaces the initial credentials with credentials configured to create files as the cache root directory’s security context. It temporarily drops the active override, calls `set_create_files_as()`, installs the new credentials, reapplies override, and checks whether mkdir/create are permitted in the root.
- `cachefiles_check_cache_dir()` uses LSM hooks `security_inode_mkdir()` and `security_inode_create()` to validate create permissions.

Usage model:
- Callers use `cachefiles_begin_secure()` and `cachefiles_end_secure()` from `internal.h` to override current credentials while manipulating backing cache files.
- Security setup happens during `cachefiles_add_cache()` before directories are created/opened.

Important behavior:
- If `security_inode_mkdir()` returns `-EOPNOTSUPP`, cache security determination treats that as acceptable.
- Failed LSM context selection or create-as setup prevents cache registration.
