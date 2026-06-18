# sources/security-integrity/cryfs/crates/fsblobstore/src/fsblobstore/fsblob/dir_entries/entry.rs

Purpose: Defines the serialized directory entry record and validation rules.

Important APIs/types/functions: `EntryType` maps dir/file/symlink to one byte. `DirEntryImpl` is the binrw-serialized layout. `DirEntry` wraps it to enforce validation through `new`, `deserialize`, and `serialize`. Getters/setters expose type, mode, uid/gid, access/modification/metadata-change times, name, and blob id. `ValidationFailed` reports mismatched mode type bits.

Control flow: construction normalizes mode by setting the type bit for the entry type, then validates that exactly the matching file/dir/symlink bit is present. `set_mode` rolls back if validation fails. Path components are serialized as null-terminated nonzero bytes and parsed back through UTF-8 plus `PathComponentBuf` validation.

State and persistence behavior: persisted fields include type, mode, uid, gid, atime, mtime, ctime, name, and blob id. Changing metadata updates ctime; changing atime does not. The code comments question whether mtime should update ctime.

Dependencies and integration points: used exclusively through `DirEntryList` and exported by `dir_entries/mod.rs`. Depends on `binrw`, `BlobId`, fs types, binary timestamp helpers, and CryFS path validation.

Risks: corrupt UTF-8 or invalid path components fail deserialization. `serialize` uses `expect` if an invariant is broken. The separate `EntryType` and `BlobType` enums must remain semantically aligned.

Test signals: TODO comments call out missing tests for path component read/write. Additional coverage should validate mode-bit rejection, ctime update semantics, and malformed serialized entries.
