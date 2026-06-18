## sources/user-network-fs/go-fuse/fuse/pathfs/default.go

Purpose: null implementation of deprecated pathfs `FileSystem`.

Important APIs/types/functions: `NewDefaultFileSystem` returns `defaultFileSystem`; methods return `ENOSYS`, `ENOENT`, empty xattr values, no-op mount hooks, and nil statfs as appropriate.

Control flow: user path filesystems embed it and override only supported path operations.

State and persistence: stateless.

Dependencies and integration: baseline for pathfs examples and wrappers.

Risks and test signals: default errno choices affect kernel feature probing and read-only behavior. Compile coverage ensures it satisfies the full interface.
