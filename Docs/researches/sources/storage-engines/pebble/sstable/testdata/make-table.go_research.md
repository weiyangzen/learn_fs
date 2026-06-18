# sources/storage-engines/pebble/sstable/testdata/make-table.go

## Purpose
Regenerates SSTable fixture files from `sstable.TestFixtures`.

## Important APIs, Types, And Functions
`main` validates it is run from the `testdata` directory, changes to the parent `sstable` directory so relative fixture paths work, iterates `sstable.TestFixtures`, and calls `fixture.Build`.

## Control Flow
The program reads the working directory, asserts the base name is `testdata`, changes up one level, prints each generated filename, and writes it through the default VFS.

## State And Persistence Behavior
Persists fixture SST files under `testdata/<fixture.Filename>`. It does not create commits or update metadata beyond those files.

## Dependencies And Integration Points
Depends on `sstable.TestFixtures`, `vfs.Default`, and CockroachDB errors. It is invoked by the Makefile.

## Risks And Edge Cases
Running from the wrong directory panics. Fixture byte output depends on current writer implementation and compression libraries.

## Test Signals
Console "Generating ..." lines and successful completion indicate regeneration; `writer_fixture_test.go` validates byte equality.
