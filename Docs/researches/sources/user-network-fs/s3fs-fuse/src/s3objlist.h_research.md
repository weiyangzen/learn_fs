# sources/user-network-fs/s3fs-fuse/src/s3objlist.h

Purpose: declares object-list structures and the `S3ObjList` class used to represent S3 listing results in filesystem-friendly form.

Important APIs and types: `s3obj_entry` stores normalized/original names, ETag, size, last-modified, and object type. `s3obj_t`, `s3obj_list_t`, and `s3obj_type_map_t` define map/list contracts. `S3ObjList` exposes insertion, metadata lookup, common prefix access, name list/map extraction, existence/removal, debug dumping, and `MakeHierarchizedList`.

Control flow: callers construct a list, insert objects as XML pages are parsed, then query names and metadata to fill directory entries or stat caches. Private helpers keep canonicalization details inside the class.

State and persistence: all state is in memory in `objects` and `common_prefixes`. The class does not provide locking, so callers must avoid concurrent mutation or guard externally.

Dependencies and integration points: relies on `types.h` for `objtype_t`; used by XML parsing, multi-head/stat fill code, and directory listing code.

Risks: because the class mixes canonical entries and normalization aliases in one map, callers must understand `OnlyNormalized` behavior. Lack of locking is fine for per-request objects but unsafe if shared. Metadata defaults (`size = -1`, empty last-modified) must be handled by consumers.

Test signals: class-level tests for every public method, especially alias filtering, common prefix retention, and directory type classification.
