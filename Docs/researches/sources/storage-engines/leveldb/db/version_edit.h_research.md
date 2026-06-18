# sources/storage-engines/leveldb/db/version_edit.h

Purpose: defines `FileMetaData` and `VersionEdit`, the in-memory representation of table-file metadata and descriptor-log mutations.

Important APIs and types: `FileMetaData` fields `refs`, `allowed_seeks`, `number`, `file_size`, `smallest`, `largest`; `VersionEdit::SetComparatorName`, `SetLogNumber`, `SetPrevLogNumber`, `SetNextFile`, `SetLastSequence`, `SetCompactPointer`, `AddFile`, `RemoveFile`, `EncodeTo`, `DecodeFrom`, and `DebugString`.

Control flow: users build an edit by setting optional metadata and adding/removing file operations; `VersionSet::LogAndApply` fills missing log/sequence fields, applies it to a builder, persists it, and installs a new `Version`.

State and persistence behavior: `FileMetaData` is reference-counted by live `Version`s and records seek budget for seek-triggered compaction. `VersionEdit` contains flags for optional scalar fields, vectors for compact pointers and new files, and a set for deleted files.

Dependencies and integration: includes `dbformat.h` for internal keys and sequence types. `VersionSet` is a friend and directly reads private fields during apply/recover.

Risks and edge cases: `AddFile` assumes smallest/largest are accurate and the edit has not already been saved. Incorrect metadata can corrupt lookup and compaction behavior. `RemoveFile` is level-specific.

Test signals: encode/decode unit tests cover field persistence but not semantic validation of file ranges.
