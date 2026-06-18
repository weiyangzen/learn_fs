# sources/user-network-fs/nfs-utils/support/export/export.c

## Purpose
Maintains the in-core export list parsed from `/etc/exports`, `/etc/exports.d`, and etab state. It binds parsed `exportent` records to cached clients and indexes them by client type and path hash.

## Important APIs, Types, and Functions
Important APIs include `export_read()`, `export_d_read()`, `export_create()`, `export_lookup()`, `export_find()`, `export_freeall()`, `exportent_realpath()`, `exportent_release()`, and `export_test()`. Internal helpers duplicate exports, insert into `exportlist`, compute simple path hashes, and warn about duplicate export entries.

## Control Flow
`export_read()` iterates `getexportent()`, looks for an existing host/path export, creates new records, warns on duplicates, and rejects manual numeric fsid assignments when any `reexport=` option is present. `export_find()` searches all client classes for a caller/path match and duplicates non-FQDN exports into FQDN-specific exports. `export_test()` writes a test line to the nfsd export cache channel.

## State and Persistence Behavior
`exportlist[MCL_MAXTYPES]` is the process-global export index with linked-list heads and hash buckets. Each `nfs_export` owns a duplicated `exportent`, flags for xtab/export status, and a counted client reference. Real paths are lazily cached in `e_realpath` and released by `exportent_release()`.

## Dependencies and Integration Points
Depends on `nfslib.h` export parser APIs, `exportfs.h` client/export types, `nfsd_path` rootdir helpers, `xmalloc`, logging, and reexport policy. It integrates with `xtab.c`, `v4root.c`, auth/cache upcall processing, and exportfs CLI operations.

## Risks and Edge Cases
The path hash is simple and collision handling depends on linked-list bucket boundaries. Duplicate exports with incompatible flags are ignored after logging. Reexport/fsid validation is global after parsing. `export_test()` relies on procfs cache channels and buffer sizing.

## Test Signals
Use parser tests for duplicate exports, exports.d filtering and version sorting, chroot rootdir realpath handling, reexport with manual fsid rejection, wildcard-to-FQDN duplication, hash collisions, and kernel export test success/failure.
