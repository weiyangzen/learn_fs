# sources/user-network-fs/samba/source3/lib/idmap_cache.h

Purpose: declares idmap cache lookup, set, and deletion functions.

Important APIs/types/functions: SID-to-unixid/uid/gid lookups, XID-to-SID lookup, setter, and UID/GID/SID delete helpers.

Control flow: callers resolve from cache, update after mapping, and invalidate when external mapping state changes.

State/persistence behavior: functions mutate or read gencache-backed persistent entries and return expiration flags.

Dependencies/integration: used by idmap/winbind and id-cache invalidation code.

Risks/test signals: callers must interpret negative mappings correctly. Compile and idmap-cache torture coverage validate the API.
