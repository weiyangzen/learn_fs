# sources/user-network-fs/go-fuse/fs/dirstream_test.go

Purpose: focused test for list-backed `DirStream` seek behavior through a mounted filesystem.

Important types/functions: `SimpleFS.Readdir` returns 16 deterministic regular-file entries through `NewListDirStream`; `TestDirSeek` mounts `SimpleFS`, defers cleanup/unmount, and invokes shared `testDirSeek` from `dir_test.go`.

State/dependencies: real FUSE mount plus deterministic in-memory directory entries.

Risks/test signals: validates that the generic list stream path cooperates with bridge/loopback directory seeking. It relies on helper behavior in `dir_test.go`; failures point to offset management rather than filesystem content generation.
