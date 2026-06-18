# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/symlink_blob.rs

Purpose: Represents symlink blobs whose data payload is the target string.

Important APIs/types/functions: `create_blob` writes a `BlobType::Symlink` blob with target bytes. `target` reads all data and decodes UTF-8. Other APIs expose blob id, parent, parent update, removal, `lstat_size`, `flush`, block enumeration, and test helpers.

Control flow: reading the target loads the full base data payload every time and converts it to `String`. Size is recomputed from the decoded target string length. Removal delegates directly to `BaseBlob::remove`.

State and persistence behavior: symlink target is persisted as UTF-8 bytes after the common header; ownership/timestamps live in parent directory entries. There is no target cache.

Dependencies and integration points: constructed by `FsBlobStore`, parsed by `FsBlob`, and referenced by directory entries with `EntryType::Symlink`.

Risks: invalid UTF-8 in the blob fails target reads and lstat size. Very large symlink data is read entirely; a TODO notes the lack of max-size enforcement. `lstat_size` rereads the target.

Test signals: tests should cover UTF-8 failure, target round-trip, lstat size, parent update, and remove behavior.
