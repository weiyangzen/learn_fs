# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/seq_write_large_file_test.go

Purpose: integration test for sequentially writing a 500 MiB file through gcsfuse.

Important APIs/types/functions: constants `FiveHundredMB`, `ChunkSize`, `DirForSeqWrite`, variable `FiveHundredMBFile`, and `TestWriteLargeFileSequentially`.

Control flow: creates a mounted test directory, builds matching local and mounted paths, writes both sequentially in 20 MiB chunks, then compares file content.

State/persistence behavior: writes a large local temp file and a large mounted object; removes only the local temp file in cleanup.

Dependencies/integration: core test for write-large-files package setup and operations helpers.

Risks/test signals: the generated `FiveHundredMBFile` is package-global, so all tests in the process share that name. Signal is byte-for-byte equality after sequential write completion.
