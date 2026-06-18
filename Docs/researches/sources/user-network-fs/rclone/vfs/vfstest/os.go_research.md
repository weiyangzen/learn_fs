# sources/user-network-fs/rclone/vfs/vfstest/os.go

## Purpose
Defines the `Oser` abstraction and a real-OS implementation so the same tests can run against either mounted paths or in-process VFS.

## APIs, Flow, And State
`Oser` lists filesystem operations needed by tests. `realOs` delegates to `os` and `lib/file` helpers. `realOsFile` wraps `*os.File` to satisfy `vfs.Handle`, adding no-op `Flush`, `Release` as close, nil `Node`, and invalid lock methods.

## Dependencies And Integration
Used by `Run.startMountSubProcess` for non-direct VFS mode. The interface aligns real OS handles with VFS handles so test code can remain transport-neutral.

## Risks And Test Signals
Adapter methods must preserve close semantics across `Close`, `Flush`, and `Release`. Misalignment can make tests pass in one mode and fail in another. Compile-time interface assertions guard basic compatibility.
