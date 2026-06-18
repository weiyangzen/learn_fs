# sources/user-network-fs/go-fuse/fs/inmemory_example_test.go

Purpose: example of constructing a static in-memory filesystem with persistent inodes.

Important types/functions: global `files` maps paths to content; `inMemoryFS.OnAdd` walks path components, creates persistent directory inodes, creates `fs.MemRegularFile` leaves, and attaches children. `Example` mounts the root with debug enabled and waits.

State/dependencies: all file data persists in memory for the lifetime of the mount; no backing disk except temporary mount directory.

Integration/risks: demonstrates `NodeOnAdder`, `NewPersistentInode`, `AddChild`, and `MemRegularFile`. Risks are memory growth for large static trees and lack of cleanup beyond unmount. Build/example execution is the test signal.
