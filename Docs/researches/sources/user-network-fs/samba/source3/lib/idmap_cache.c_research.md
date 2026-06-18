# sources/user-network-fs/samba/source3/lib/idmap_cache.c

Purpose: caches SID-to-Unix-ID and Unix-ID-to-SID mappings, including negative results, in gencache.

Important APIs/types/functions: SID-to-unixid/uid/gid lookups, XID-to-SID lookup, `idmap_cache_set_sid2unixid()`, and delete helpers for UID/GID/SID.

Control flow: SID lookup parses values like `<id>:U/G/B/N`; XID lookup parses SID strings or `-` negative markers. Set writes forward and reverse keys according to SID/null-SID and id/type. Delete removes symmetric reverse and forward entries where present.

State/persistence behavior: keys are `IDMAP/SID2XID/<sid>`, `IDMAP/UID2SID/<id>`, and `IDMAP/GID2SID/<id>` with positive or negative cache timeouts from loadparm.

Dependencies/integration: depends on gencache, SID conversion, generated idmap `struct unixid`, and winbind/idmap consumers. Torture tests cover basic behavior.

Risks/test signals: stale asymmetric mappings, malformed values, type confusion, and negative-cache lifetime are risks. Tests should cover UID/GID/BOTH, negative mappings, expiry, and all delete paths.
