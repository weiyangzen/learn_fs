# sources/storage-engines/rocksdb/utilities/checkpoint/checkpoint_impl.h

## Purpose
This header declares `CheckpointImpl`, the concrete implementation of the public RocksDB checkpoint utility.

## Important APIs, Types, and Functions
`CheckpointImpl` derives from `Checkpoint` and stores a raw `DB*`. It overrides `CreateCheckpoint` and `ExportColumnFamily`. It also declares `CreateCustomCheckpoint`, which lets callers customize link, copy, and file-creation behavior. Private helpers are `CleanStagingDirectory` and `ExportFilesInMetaData`.

## Control Flow
The header defines the extension points used by the implementation. `CreateCustomCheckpoint` accepts callback functions for each file action and options for sequence output, WAL flush threshold, checksum collection, and atomic flush behavior.

## State and Persistence Behavior
The implementation object does not own the DB; callers must keep the DB alive. Persistent effects are all through the underlying DB environment and filesystem when checkpoint/export methods are invoked.

## Dependencies and Integration Points
It depends on RocksDB DB APIs, filename parsing types, and the public checkpoint utility header. The callback signatures expose `FileType`, checksum strings, file size limits, and `Temperature`, making checkpoint logic reusable by backup-like code.

## Risks and Edge Cases
The raw `DB*` lifetime is not protected. Callback contracts must correctly preserve file contents, truncation limits, checksums, and directory fsync requirements, or generated checkpoints can be non-openable. `CreateCustomCheckpoint` is powerful enough for tests and backup code but easy to misuse.

## Test Signals
Compile and behavior coverage comes from `checkpoint_test.cc` and backup tests using the same live-file metadata machinery. Tests that mock custom callbacks are especially useful for link/copy fallback and checksum propagation.
