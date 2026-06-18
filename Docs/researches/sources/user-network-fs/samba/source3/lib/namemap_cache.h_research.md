# sources/user-network-fs/samba/source3/lib/namemap_cache.h

## sources/user-network-fs/samba/source3/lib/namemap_cache.h

Purpose: Declares the public source3 name-map cache API for bidirectional SID/name cache operations.

Important APIs/types/functions: Exposes set/find functions for `sid2name` and `name2sid`. Find calls are callback-based and return parsed `domain`, `name`, `lsa_SidType`, `dom_sid`, and an `expired` flag.

Control flow: Callers set cache entries with a timeout and later request parsed values by key. The header leaves persistence details to `namemap_cache.c`.

State and persistence behavior: The API describes gencache-backed state indirectly through timeout and expired reporting. Ownership of callback values is transient.

Dependencies and integration points: Includes `replace.h`, `time.h`, `dom_sid`, and generated LSA SID type definitions. Used by authentication/name lookup layers.

Risks: Callback consumers must not retain transient pointers without copying. Passing NULL or null SID has special behavior in implementation.

Test signals: Compile users plus cache torture tests should verify all four declarations and callback signatures.
