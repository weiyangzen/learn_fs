# File Research: sources/os/linux/linux/fs/cachefiles/security.c

## Purpose
Builds and adjusts the credentials CacheFiles uses for kernel-side VFS access to the backing cache.

## Main Elements
- `cachefiles_get_security_ID()`: prepares kernel credentials from the current task and optionally applies the daemon-specified LSM security ID.
- `cachefiles_check_cache_dir()`: asks LSM hooks whether mkdir and create are permitted in the cache root.
- `cachefiles_determine_cache_security()`: derives create-file credentials from the backing cache root inode, replaces `cache->cache_cred`, restores the override, and validates directory permissions.

## Dependencies And Integration
Works with daemon `secctx` configuration, LSM credential APIs, and credential override helpers in `internal.h`. Called during cache binding before CacheFiles creates backing directories and files.

## Risk Notes
Credential replacement deliberately drops and reapplies override credentials while deriving file-creation security. Security hook failures prevent cache binding unless unsupported create-file-as behavior is treated as acceptable.
