# sources/user-network-fs/s3fs-fuse/src/s3objlist.cpp

Purpose: implements `S3ObjList`, the in-memory normalized list of S3 objects returned by listing operations, including directory-object normalization, metadata lookup, list/map extraction, removal, dumping, and hierarchy synthesis.

Important APIs and functions: `insert` normalizes names, directory markers, ETag, size, and last-modified data. `insert_normalized` records alias entries. Lookup helpers include `GetOrgName`, `GetNormalizedName`, `GetETag`, `GetSize`, `GetLastModified`, `IsDir`, `GetLastName`, `GetNameList`, `GetNameMap`, `HasName`, and `Remove`. `Dump` serializes debug state. `MakeHierarchizedList` adds missing parent directory entries to a flat list.

Control flow: XML parsing inserts objects or common prefixes. `insert` detects `_$folder$`, trailing slash, and explicit directory flags, removes conflicting file-vs-directory variants, stores canonical entries, then records original-to-normalized mappings when needed. Name extraction optionally filters alias entries and trims trailing slashes. Hierarchy synthesis builds a map of existing and inferred parent directories before appending missing parents.

State and persistence: object state is stored in `objects`, a map keyed by original/canonical names, with `s3obj_entry` values for normalized name, original name, ETag, size, last-modified, and type. `common_prefixes` preserves prefix entries separately. No disk persistence.

Dependencies and integration points: depends on `objtype_t` helpers/macros from `types.h`, and is populated primarily by `s3fs_xml.cpp`. Consumers include directory listing, stat cache filling, and sync filler paths.

Risks: `HasName` and `Remove` appear to compute the no-slash form incorrectly for names ending in `/` by using `substr(strName.size() - 1)`, yielding just `/` rather than removing the trailing slash. Empty `strName` passed to those functions calls `back()` and is undefined. Normalization aliases can make map contents non-obvious, so list/map extraction must consistently filter aliases. Directory-vs-file conflict removal is semantic-critical for S3-compatible directory behavior.

Test signals: insertion tests for files, `dir/`, `dir`, `dir_$folder$`, duplicate updates, alias lookup, ETag/size/last-modified preservation, `HasName`/`Remove` with trailing and non-trailing slash, empty-name defensive behavior, `GetLastName`, and hierarchy synthesis with and without slash suffixes.
