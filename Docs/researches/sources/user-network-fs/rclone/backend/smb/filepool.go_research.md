# sources/user-network-fs/rclone/backend/smb/filepool.go

## Purpose

`filepool.go` supports SMB random-access writes by pooling open write handles to one target file. It is used by `OpenWriterAt` for concurrent `WriteAt` calls.

## Important APIs, Types, and Functions

`FsInterface` abstracts the subset of `Fs` needed by the pool. `file` couples an `*smb2.File` with its owning `conn`. `filePool` stores context, backend interface, share, path, mutex, and pooled handles. `newFilePool` constructs the pool. `get` returns an existing handle or opens one through a borrowed connection. `put` returns a healthy handle to the pool or closes/returns its connection with an error. `drain` closes all pooled handles concurrently and returns their connections.

## Control Flow

`smbWriterAt.WriteAt` asks the pool for a file handle, writes at an offset, and returns the handle with the write error. On an empty pool, `get` borrows a connection for the target share and opens the path write-only. On close, `smbWriterAt.Close` waits for writes, drains the file pool, and decrements the SMB session count.

## State and Persistence Behavior

The pool owns open file handles and their associated borrowed connections until drained or discarded. It has no persistent state; remote persistence is the target SMB file contents.

## Dependencies and Integration Points

It depends on `go-smb2` file handles and `errgroup`. `smb.go` uses it exclusively through `smbWriterAt` returned by `OpenWriterAt`.

## Risks and Edge Cases

A write error closes only that handle and probes/returns its connection through `putConnection`; other pooled handles may still exist. `drain` closes pooled idle handles but not handles currently checked out; `smbWriterAt.Close` coordinates this by waiting for its `WaitGroup`. Mock tests use zero-value `smb2.File`, so they do not validate real close errors.

## Test Signals

`filepool_test.go` covers construction, reuse, empty-pool error propagation, error discard, nil puts, drain, and concurrent get/put consistency. Integration signal comes from parallel multipart or VFS random writes through SMB.
