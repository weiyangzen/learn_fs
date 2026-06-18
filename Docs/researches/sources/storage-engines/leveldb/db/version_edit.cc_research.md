# sources/storage-engines/leveldb/db/version_edit.cc

Purpose: serializes and parses `VersionEdit` records, the persistent mutation format for MANIFEST descriptors. Each record updates metadata such as comparator name, log numbers, next file number, last sequence, compaction pointers, deleted files, and added table files.

Important APIs and functions: enum `Tag`, `VersionEdit::Clear`, `EncodeTo`, `DecodeFrom`, `DebugString`, helper `GetInternalKey`, and helper `GetLevel`.

Control flow: `EncodeTo` emits only fields with `has_*` flags plus repeated compact pointer, deleted file, and new file entries. `DecodeFrom` clears the object, loops over varint tags, reads typed payloads, validates levels and internal keys, and returns `Status::Corruption` on unknown or malformed fields.

State and persistence behavior: tag numbers are on-disk format and must not change. Added file metadata records include level, number, file size, smallest internal key, and largest internal key. Deleted files are stored in an ordered set, giving deterministic re-encoding.

Dependencies and integration: uses `util/coding` varint and length-prefixed encodings, `InternalKey::Encode/DecodeFrom`, `config::kNumLevels`, and `VersionSet::Builder` application logic.

Risks and edge cases: unknown future tags are fatal rather than skipped, so format evolution requires compatibility care. Decode does not validate non-overlap or file-number monotonicity; those are enforced later by `VersionSet`. Partial records leave the edit cleared or partially filled but return corruption.

Test signals: `version_edit_test.cc` round-trips large values, repeated file additions/removals, and compact pointers, giving deterministic encode/decode coverage.
