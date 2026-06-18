# sources/storage-engines/leveldb/db/version_edit_test.cc

Purpose: validates that `VersionEdit` encoding and decoding are stable and deterministic.

Important APIs and functions: `TestEncodeDecode` and test `VersionEditTest.EncodeDecode`.

Control flow: the helper encodes an edit, decodes into a fresh object, re-encodes, and asserts byte equality. The test progressively adds files, removals, compact pointers, and scalar metadata with large 50-bit values.

State and persistence behavior: exercises the MANIFEST record byte format, especially varint64 values and repeated entries.

Dependencies and integration: depends on `InternalKey`, `kTypeValue`, `kTypeDeletion`, and gtest. It directly protects compatibility of `version_edit.cc`.

Risks and edge cases: it does not test malformed input, unknown tags, invalid levels, duplicate delete entries, or comparator mismatch handling.

Test signals: strong round-trip signal for normal descriptor edits and large numeric values.
