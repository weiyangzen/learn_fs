# sources/user-network-fs/samba/source3/lib/namemap_cache.c

## sources/user-network-fs/samba/source3/lib/namemap_cache.c

Purpose: Caches SID-to-name and name-to-SID mappings in Samba gencache for name lookup acceleration.

Important APIs/types/functions: `namemap_cache_set_sid2name()`, `namemap_cache_find_sid()`, `namemap_cache_set_name2sid()`, and `namemap_cache_find_name()` are exported. Parser state structs carry caller callbacks and parse status. Values are stored as Samba string vectors containing domain/name/type or sid/type.

Control flow: Set functions normalize NULL inputs, handle unknown SID types specially, construct keys `SID2NAME/<sid>` or uppercase `NAME2SID/<domain>\<name>`, serialize fields with `strv_add()`, and call `gencache_set_data_blob()`. Find functions call `gencache_parse()`, parse string-vector fields, validate SID/type conversion, invoke the caller callback with an expired flag, and delete corrupt SID2NAME entries.

State and persistence behavior: Data persists in gencache until timeout. Expired entries can still be returned with an explicit expired boolean. Corrupt SID2NAME entries are deleted; corrupt NAME2SID entries fail lookup but are not explicitly deleted in this function.

Dependencies and integration points: Integrates with winbind/name lookup code, `gencache`, `dom_sid` parsing/formatting, talloc stack, charset uppercasing, `smb_strtoul`, and debug logging.

Risks: Uppercasing controls name-key canonicalization and must stay locale/charset-safe. Unknown SID type stores empty identity. Callback contracts must tolerate expired values. Corrupt cache data can cause lookup misses.

Test signals: `source3/torture/test_namemap_cache.c` is the direct test target. Coverage should include NULL domain/name, unknown types, expired entries, invalid blobs, invalid SID/type fields, and case-insensitive name lookup.
