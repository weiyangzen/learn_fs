# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry_list.rs

Purpose: Implements the mutable in-memory directory entry collection and its serialization.

Important APIs/types/functions: `DirEntryList` stores a sorted `Vec<DirEntry>` plus a dirty flag. APIs include lookup by name/id, deserialize, serialize-if-dirty, iteration, add, add-or-overwrite, rename, set attributes, maybe update atime, update mtime, remove by name, and remove by id. Error enums model add, overwrite, set-attr, timestamp, remove, and rename failures.

Control flow: id lookups use a hinted linear lower/upper-bound search based on random blob-id bytes. Name lookups are linear. Adds insert by blob-id order. Overwrite removes and re-adds if the blob id changes. Rename can invoke an overwrite callback before deleting the target name, then mutates the source name in place.

State and persistence behavior: dirty is set on mutable access and all structural mutations. Serialization rewrites the complete directory data payload after resizing the base blob; after success dirty is cleared. Deserialization reads the whole directory payload into a cursor.

Dependencies and integration points: owned by `DirBlob`; uses `DirEntry`, `EntryType`, `BaseBlob`, fs uid/gid/mode types, and `AtimeUpdateBehavior`.

Risks: comments document a no-hardlink invariant: at most one entry per blob id. `get_by_name_mut` marks dirty before the caller actually changes anything. Deserialization does not explicitly sort or deduplicate entries, so corrupted ordering could break id lookup assumptions. Full rewrite can be costly for large directories.

Test signals: key tests should include sorted insertion, corrupted unsorted input behavior, overwrite callback failures, rename-over-existing, dirty flag serialization, and atime policy branches.
