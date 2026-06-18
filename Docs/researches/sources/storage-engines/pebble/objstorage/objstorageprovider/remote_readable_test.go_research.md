# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable_test.go

Purpose: This file tests remote read-handle buffering/readahead behavior and corruption conversion when an opened remote object disappears.

Important types and tests: `testObjectReader` is a deterministic in-memory `remote.ObjectReader` that logs each `ReadAt` and `Close`. `TestRemoteReadHandle` is data-driven over `testdata/remote_read_handle`; it initializes a readable, creates read handles with a chosen `read-before-size`, optionally calls `SetupForCompaction`, performs reads, checks returned bytes, and emits the underlying remote read trace. `TestErrorWhenObjectDisappears` builds a real provider with in-memory remote storage, creates a shared object, opens it, deletes all underlying remote objects, and verifies the subsequent read returns a Pebble corruption error.

Control flow and state: The data-driven test keeps one reader/readable/read-handle across commands and closes old handles/readables as new ones are created. It directly observes whether a logical read became one larger remote read, a buffered hit, or an EOF.

Dependencies and integration: It uses `remote.NewInMem`, `remote.MakeSimpleFactory`, `DefaultSettings`, `Provider.Create`, `OpenForReading`, and `base.IsCorruptionError`. It does not use shared cache in the read-handle trace path.

Risks and test signals: The tests catch regressions in read-before one-shot semantics, compaction readahead, buffer prefix handling, EOF reporting, and conversion of remote not-exist errors into corruption. They do not measure memory accounting or cache write-back behavior.
