# sources/storage-engines/tikv/patches/tempdir/src/lib.rs

## Purpose
Implements a small `tempdir::TempDir` compatibility wrapper on top of `tempfile::Builder`. It preserves the familiar API shape while relying on `tempfile` for secure directory creation.

## Important APIs and Control Flow
`TempDir` stores `path: Option<PathBuf>`. `new(prefix)` delegates to `new_in(env::temp_dir(), prefix)`. `new_in(tmpdir, prefix)` normalizes relative bases against `env::current_dir()`, creates a temporary directory with `tempfile::Builder::prefix(prefix).tempdir_in(base)`, and stores the path after `tempfile::TempDir::into_path()`. `path()` returns the owned path, `into_path()` transfers ownership to the caller, and `close()` removes the directory with `fs::remove_dir_all`. `AsRef<Path>`, `Debug`, and `Drop` round out the compatibility API.

## State and Persistence
`Some(path)` means the wrapper owns cleanup. `into_path` takes the path and makes it persistent beyond the wrapper. `close` consumes the wrapper, removes the directory, clears ownership, and returns the deletion result. `Drop` best-effort removes the directory if ownership remains.

## Dependencies and Integration Points
Uses `std::env`, `std::fmt`, `std::fs`, `std::io`, `std::path`, and `tempfile`. It integrates with code importing `tempdir::TempDir` through the local patch crate.

## Risks and Test Signals
Cleanup errors are ignored in `Drop`; callers needing errors must use `close`. `path().unwrap()` and `into_path().unwrap()` rely on ownership flow and would panic after internal clearing. Tests should cover creation, drop cleanup, explicit close, survival after `into_path`, relative bases, and `AsRef`/`Debug` behavior.
