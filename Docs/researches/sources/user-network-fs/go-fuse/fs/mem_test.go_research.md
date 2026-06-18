## sources/user-network-fs/go-fuse/fs/mem_test.go

Purpose: exercises the modern `fs` in-memory node helpers and shared test mount helper. It verifies ownership defaults, explicit root inode numbers, `MemRegularFile` read/write/stat behavior, large reads, symlink construction, readdirplus consistency, and a POSIX subset over an in-memory writable directory.

Important APIs/types/functions: `testMount` wraps `Mount`, configures debug logging, waits for mount, and registers cleanup. `SymlinkerRoot.Symlink` creates `MemSymlink` persistent inodes. `readDirStream` drains `DirStream`. `memDir.Create` creates handleless `MemRegularFile` children. Tests call `NewPersistentInode`, `AddChild`, `NewLoopbackDirStream`, `posixtest`, and `fuse.Attr`.

Control flow: each test builds a root `Inode`, often populates children via `Options.OnAdd`, mounts into `t.TempDir`, performs kernel-facing syscalls through the mount, then unmounts through cleanup. Readdir tests compare parsed kernel directory streams across many concurrent readers. `TestMemPosix` iterates selected POSIX scenarios and remounts per subtest.

State and persistence: data is process-memory state stored in `MemRegularFile.Data` and inode child maps; no durable persistence is expected. Timeouts influence kernel entry/attribute caching. `FirstAutomaticIno`, `RootStableAttr`, UID/GID options, and stable attrs determine visible inode metadata.

Dependencies and integration: integrates `fs.Mount`, `fuse.Server`, `fuse.Attr`, `internal/testutil`, and `posixtest`. It is a regression suite for the high-level inode API and for compatibility with kernel syscall behavior.

Risks and test signals: concurrency-sensitive readdirplus and POSIX tests catch races in directory stream conversion, inode lookup, and file handle paths. The tests require a working FUSE environment; failures may reflect mount permissions or kernel behavior rather than pure Go logic.
