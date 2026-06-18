# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/file/OMFileRequest.java

## Purpose

`OMFileRequest` is the static utility hub for Ozone filesystem request semantics. It implements legacy and FSO path traversal, directory/file conflict detection, cache and batch writes for file/directory/open-file tables, conversion between directory and key info, child detection, parent lookup, and volume/bucket validation.

## Important APIs, Types, And Functions

- `verifyFilesInPath(...)` walks legacy key-table paths from leaf upward, detecting files/directories in the requested path and collecting missing parents plus inheritable ACLs.
- `verifyDirectoryKeysInPath(...)` walks FSO path components from the bucket object ID through directory and key tables.
- `OMPathInfo`, `OMPathInfoWithFSO`, and `OMDirectoryResult` communicate traversal result, missing parents, ACLs, leaf name, parent ID, object ID, and file-conflict path.
- Cache helpers: `addKeyTableCacheEntries`, `addDirectoryTableCacheEntries`, `addOpenFileTableCacheEntry`, `addFileTableCacheEntry`.
- Batch helpers: `addToOpenFileTable`, `addToOpenFileTableForMultipart`, `addToFileTable`.
- Lookup/conversion helpers: `getOmKeyInfoFromFileTable`, `getOMKeyInfoIfExists`, `getKeyInfoWithFullPath`, `getOmKeyInfo`, `getDirectoryInfo`, `getAbsolutePath`.
- Rename/delete helpers: `verifyToDirIsASubDirOfFromDirectory`, `getKeyParentDir`, `hasChildren`, `getParentID`, `getParentId`, `validateBucket`.

## Control Flow And State

The class itself has no mutable global state. Its methods read and write OM metadata tables. Legacy traversal uses ozone key and dir-key encodings in the key table. FSO traversal uses volume ID, bucket ID, parent object ID, and node name against directory and file tables. Cache write helpers add either values or tombstones at the transaction index, while batch helpers persist rows during double-buffer flush. Child detection scans cache first, then seeks DB by parent path key prefix and ignores DB rows tombstoned in cache.

## Dependencies And Integration Points

`OMFileRequest` is shared by directory create, file create, commit, rename, multipart, delete, and lease-recovery paths. It depends on `OMMetadataManager`, `OmBucketInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OzoneFileStatus`, `OzoneFSUtils`, RocksDB table iterators/cache, bucket layout resolution, and Ozone exception result codes.

## Risks And Test Signals

This is a high-blast-radius utility. Tests should cover legacy and FSO path traversal, trailing slash behavior, ACL inheritance from bucket or closest parent, file-versus-directory conflicts, cache tombstone masking, immediate child detection, parent ID errors, absolute path construction, full-path restoration for FSO file info, multipart/open-file key composition, and volume-not-found versus bucket-not-found error selection.
