## sources/user-network-fs/go-fuse/fuse/nodefs/files.go

Purpose: built-in nodefs `File` implementations for memory data, `/dev/null`, loopback files, locks, and read-only wrappers.

Important APIs/types/functions: `NewDataFile`, `dataFile.Read/GetAttr`; `NewDevNullFile`; `NewLoopbackFile`, `loopbackFile` read/write/release/flush/fsync/locks/truncate/chmod/chown/getattr; `NewReadOnlyFile` and `readOnlyFile` deny mutating operations.

Control flow: loopback reads return `fuse.ReadResultFd` for zero-copy reads, writes use `WriteAt`, flush closes a dup fd, release closes the real file, and lock operations map FUSE locks to `flock` or OFD `fcntl` locks.

State and persistence: loopback file state is an `*os.File` protected by a mutex. DataFile stores immutable bytes in memory. ReadOnlyFile wraps inner state.

Dependencies and integration: used by nodefs loopback/pathfs and tests. Platform-specific files add allocation and utimens.

Risks and test signals: fd reuse races and close/read concurrency are core risks; mutexes and tests around fd leaks and locks protect this behavior.
