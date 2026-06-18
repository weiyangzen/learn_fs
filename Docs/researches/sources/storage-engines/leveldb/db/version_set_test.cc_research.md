# sources/storage-engines/leveldb/db/version_set_test.cc

Purpose: unit-tests version-set helper algorithms for file search, range overlap, and compaction boundary expansion.

Important APIs and types: `FindFileTest`, `FindFileTest::Add`, `Find`, `Overlaps`, test cases for empty/single/multiple/null-boundary/sequence/overlapping files, `AddBoundaryInputsTest`, `CreateFileMetaData`, and boundary-file tests.

Control flow: file metadata is built manually with internal key ranges and checked against expected binary-search and overlap outcomes. Boundary tests construct same-user-key internal key sequences and assert `AddBoundaryInputs` extends compaction input order correctly.

State and persistence behavior: in-memory test metadata only. It models the ordering invariants required for persistent table metadata without writing a DB.

Dependencies and integration: depends on `InternalKeyComparator`, `BytewiseComparator`, `FileMetaData`, and exported test-visible `AddBoundaryInputs`.

Risks and edge cases: tests cover critical boundary cases but do not run full compaction output generation. Manual `FileMetaData` objects may omit fields irrelevant to the helper under test.

Test signals: high-value regression signal for issue-class bugs where compaction splits records for the same user key across levels.
