# sources/user-network-fs/samba/source3/lib/id_cache.c

Purpose: provides messaging-driven invalidation for ID-related caches, including idmap cache entries and username passwd-cache entries.

Important APIs/types/functions: `struct id_cache_ref`, `id_cache_ref_parse()`, `delete_getpwnam_cache()`, `id_cache_delete_from_cache()`, `id_cache_delete_message()`, and `id_cache_register_msgs()`.

Control flow: message payloads parse as `UID <n>`, `GID <n>`, SID strings, or `USER <name>`. Deletion dispatches to idmap-cache UID/GID/SID deletion or removes a `GETPWNAM_CACHE` memcache entry for usernames. Invalid messages are logged and ignored.

State/persistence behavior: no durable state in this file; effects are deletions from gencache-backed idmap cache and process-local memcache.

Dependencies/integration: depends on messaging, SID parsing, and `idmap_cache.h`.

Risks/test signals: malformed parsing can leave stale mappings or delete wrong entries. Tests should cover UID/GID/SID/USER payloads, bad payloads, and cross-process invalidation.
