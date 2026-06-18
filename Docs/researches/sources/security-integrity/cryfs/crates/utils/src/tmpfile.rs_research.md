# sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs

Purpose: Provides `TempFile`, a minimal RAII wrapper that creates a named temporary file and deletes it when the wrapper is dropped.

Important APIs and types: `TempFile::create(path)`, `TempFile::create_async(path)`, and `path()` are the public methods. The type stores a `PathBuf`.

Control flow: Synchronous creation uses `std::fs::File::create`; async creation uses `tokio::fs::File::create`. Both store the path after successful creation. `Drop` calls `std::fs::remove_file(&self.path).unwrap()`.

State and persistence behavior: The file exists on disk while the wrapper is alive and is removed during drop. The wrapper does not keep the file handle open; it only owns the path cleanup obligation.

Dependencies and integration points: Depends on standard filesystem APIs, `tokio::fs` for async creation, and `anyhow::Result`. Tests use `tempfile::TempDir`.

Risks: Drop panics if the file was already removed, permissions changed, or cleanup otherwise fails. Because no handle is kept open, other code can modify or remove the file behind the wrapper. `File::create` truncates existing files, so callers must avoid passing important paths.

Test signals: Tests verify sync and async creation, `path()` identity, and deletion after drop.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/tmpfile.rs` completely for this pass (124 lines, 3398 bytes).
