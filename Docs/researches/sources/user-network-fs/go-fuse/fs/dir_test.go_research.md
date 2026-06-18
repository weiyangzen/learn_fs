# sources/user-network-fs/go-fuse/fs/dir_test.go

Purpose: tests directory-stream error propagation, seek behavior, and fsyncdir support.

Important tests/types: `errDirStream` returns one valid entry then `EBADMSG`; `TestDirStreamError` checks error delivery with readdirplus enabled and disabled. `dirStreamSeekNode` and `listDirEntries` produce custom offsets and implement `Seekdir`; `testDirSeek` verifies resuming after each offset. `syncNode`/`syncDir` implement `FileFsyncdirer`; `TestFsyncDir` opens the mount directory and calls `fsync`.

State/dependencies: real FUSE mounts, mutable counters protected by mutex, directory streams.

Risks/test signals: validates tricky readdir offset semantics and partial-error behavior. Kernel/platform differences in directory offsets can influence failures, but the tests use controlled streams.
