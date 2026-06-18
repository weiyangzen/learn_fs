# sources/security-integrity/cryfs/crates/rustfs/examples/passthrough/dir.rs

Purpose: Implements passthrough directory operations against the host filesystem.

Important APIs/types/functions: `PassthroughDir` stores an absolute path and implements `Dir`: lookup, rename/move, entries, mkdir, rmdir, symlink, unlink, create-and-open file, and fsync. `convert_mode` adapts `Mode` to Unix `mode_t`.

Control flow: most operations clone the directory path and append a component. Unix-specific ownership and creation operations run in `spawn_blocking` when using `nix` or `std::fs`. Directory listing reads `tokio::fs::read_dir`, converts names to `PathComponent`, and maps file types.

State and persistence behavior: changes are immediate host filesystem mutations. `fsync` opens the directory and calls `sync_all` or `sync_data`.

Dependencies and integration points: integrates `PassthroughNode`, `PassthroughOpenFile`, `PassthroughSymlink`, error conversion helpers, and metadata conversion.

Risks: unknown file types panic. Some unwraps are present in mode conversion. TODOs question directory fsync correctness, dot-entry filtering, and platform portability.

Test signals: tests should cover entry listing of files/dirs/symlinks, create/remove operations, duplicate errors, fsync, and behavior with special files.
