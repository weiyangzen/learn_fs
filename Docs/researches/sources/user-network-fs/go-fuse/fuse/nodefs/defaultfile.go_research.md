## sources/user-network-fs/go-fuse/fuse/nodefs/defaultfile.go

Purpose: null `File` implementation for embedding in nodefs file objects.

Important APIs/types/functions: `NewDefaultFile` returns a `File` whose operations return `ENOSYS` or no-op values. Methods include read/write, locks, flush, release, getattr, fsync, utimens, truncate, ownership, mode, and allocation.

Control flow: user file types embed/compose this and override supported operations.

State and persistence: stateless and nil-receiver friendly.

Dependencies and integration: used by `dataFile`, `devNullFile`, custom tests, and user code.

Risks and test signals: default return codes influence kernel fallback behavior. It must continue satisfying the full `File` interface as APIs evolve.
