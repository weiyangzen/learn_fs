# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_blob.rs

Purpose: `DirBlob` represents a directory blob with cached serialized directory entries.

Important APIs/types/functions: creation APIs build normal and root directory blobs. Lookup/mutation APIs expose entries by id/name, rename, add, add-or-overwrite, remove, attribute/timestamp updates, parent updates, `writeback`, `flush`, `lstat_size`, removal, and block enumeration.

Control flow: `new` deserializes `DirEntryList` from the base blob. Mutations update the in-memory list and mark it dirty. `writeback` serializes only if dirty; `flush` writes back then flushes the base blob only when serialization occurred. Removal skips async drop because serializing a directory that is about to be deleted is unnecessary.

State and persistence behavior: directory entries are cached in memory and persisted as the base blob data. Root creation uses a caller-provided id and parent `BlobId::zero()`, then flushes immediately to fail early if storage is inaccessible. Directory `lstat_size` is a fixed 4096.

Dependencies and integration points: wraps `BaseBlob` and `DirEntryList`; exports `MODE_NEW_SYMLINK` and uses fs uid/gid/mode types. Higher filesystem code uses it for namespace mutations.

Risks: dirty directory changes are not durable until writeback/drop/flush. Parent pointers are stored but not validated on load. Rename/overwrite correctness depends on the callback removing overwritten child blobs when needed.

Test signals: tests should cover add/remove/rename serialization, overwrite callback ordering, root creation conflict, and crash-window behavior when `DontFlush` is used.
