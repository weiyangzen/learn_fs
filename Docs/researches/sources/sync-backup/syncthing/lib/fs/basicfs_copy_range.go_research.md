## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range.go

Purpose: Adapts platform copy-range implementations that require `basicFile` and exposes helpers for syscall file descriptor access.

Important APIs/types/functions: `copyRangeImplementationBasicFile`, `copyRangeImplementationForBasicFile`, `withFileDescriptors`, and `unwrap`.

Control flow: The adapter unwraps layered `File` values, type-checks both ends as `basicFile`, returns `ENOTSUP` otherwise, and calls the platform implementation. `withFileDescriptors` obtains `SyscallConn` for both files and nests `Control` callbacks to pass raw descriptors. `unwrap` repeatedly follows local `unwrap() File` interfaces.

State and persistence: Stateless helper logic, but platform implementations mutate destination file contents.

Dependencies and integration points: Used by Linux/Windows copy-range backends registered in sibling files and by the filesystem copy-range registry elsewhere.

Risks: Nested `Control` callbacks must not block in unsafe ways. Only `basicFile` is supported, so wrapped files must expose `unwrap` correctly or optimized copy falls back.

Test signals: Copy-range tests are outside this subset; behavior is indirectly validated by filesystem copy operations.
