# sources/user-network-fs/go-nfs/nfs_test.go

## Purpose

`nfs_test.go` contains integration tests for the Go NFS server using an in-memory filesystem and the real `go-nfs-client` RPC/NFS client stack. It verifies basic mount, fsinfo, create, write/read, large directory reads, rename semantics, empty directory listing, file handle cleanup, and NFS read EOF behavior.

## Important APIs, Types, and Functions

`NewTrackingFS` wraps a `billy.Filesystem` to track opened files. `trackingFS` overrides `Create`, `Open`, and `OpenFile`, while `trackingFile.Close` removes handles from the tracking map. `TestNFS` is the broad end-to-end server test. Helper `readDir` sends raw `READDIR` RPCs because the client has a `READDIRPLUS` implementation but the test also needs plain `READDIR`. Helper `nfsRead` sends raw `READ` RPCs and parses post-op attributes, count, EOF, and data. `TestReadEOF` verifies exact EOF flag semantics.

## Control Flow

`TestNFS` starts a TCP listener on a random local port, creates a tracking `memfs`, seeds `/test` so root exists, wraps the filesystem with null auth and caching handlers, starts `nfs.Serve` in a goroutine, dials via RPC, mounts `/`, and exercises operations through the client target. It validates file creation metadata, writes `hello world`, reads it back, creates 2000 files, compares both `ReadDirPlus` and raw `READDIR` results after sorting, renames one file and checks old lookup failure, then checks empty directory results. A deferred leak check fails if any tracked files remain open.

`TestReadEOF` creates a 64 KiB random file in memfs, serves it through NFS, mounts the target, and calls `nfsRead` with read ranges that are before EOF, exactly reach EOF, extend past EOF, and start at EOF. It verifies count trimming, EOF flags, and data equality.

## State and Persistence Behavior

The tests mutate only in-memory filesystems and local TCP listeners. The NFS server goroutines are not explicitly shut down; they end when the listener is closed or the process exits. The mount is unmounted via defer and RPC connections are closed. `trackingFS.open` is protected by a mutex and serves as test-only state for leak detection.

## Dependencies and Integration Points

The tests integrate `github.com/willscott/go-nfs`, `helpers.NewNullAuthHandler`, `helpers.NewCachingHandler`, `helpers/memfs`, `go-nfs-client` RPC/NFS packages, and XDR helpers. They are strong signals that server handlers, handler caching, handle translation, and client compatibility work together over real TCP rather than only through unit-level calls.

## Risks and Edge Cases

Because the server goroutine return is ignored and no readiness synchronization is used beyond dialing after goroutine start, failures can be timing-sensitive. Random file contents in `TestReadEOF` are not seeded for reproducibility, though only equality is checked. The tracking wrapper depends on every opened file's `Close` being invoked; it is useful for leaks but can produce false negatives for operations that bypass `OpenFile`. The tests do not directly cover many error mappings or symlink/write corner cases.

## Test Signals

This file is itself the main test signal for the Go NFS subset. It should be run with `go test` for the `go-nfs` package. Regressions in directory cookie handling, EOF calculation, file handle invalidation after rename, response parsing, or file closing are likely to appear here. Additional targeted tests should be added for error paths, write durability flags, symlink creation, and handler cancellation behavior.
