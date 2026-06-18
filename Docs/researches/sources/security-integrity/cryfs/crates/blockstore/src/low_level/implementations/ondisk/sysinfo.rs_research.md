
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/ondisk/sysinfo.rs

## Purpose
This helper estimates available disk space for `OnDiskBlockStore`. It provides platform-specific implementations around system calls because the desired `sysinfo` crate API was not available when copied.

## Important APIs, Types, and Functions
- `get_available_disk_space(path: &Path) -> Result<u64>` is the public wrapper.
- Unix-like `to_cpath()` converts a path to a NUL-terminated byte vector for C APIs.
- Linux/Android implementation calls `libc::statvfs64` and returns `f_bsize * f_bavail`.
- macOS/iOS implementation calls `libc::statfs` and returns `f_bsize * f_bavail`.
- Windows implementation calls `GetDiskFreeSpaceExW` and returns `*size.QuadPart()`.

## Control Flow
Each platform implementation calls the OS API, checks the success return value with `ensure!`, and converts failure to an `errno` error. The public function simply delegates to the cfg-selected implementation.

## State and Persistence Behavior
No persistent state. It is a synchronous filesystem query used by `OnDiskBlockStore::estimate_num_free_bytes()`.

## Dependencies and Integration Points
Depends on `libc` on Unix-like systems, `winapi` on Windows, `errno`, and `anyhow::ensure`. Integrated only by the on-disk backend.

## Risks and Edge Cases
- The Windows implementation appears broken: it uses `path.as_ptr()` on `Path`, binds `(size, retval)`, but returns `(stat, retval)` where `stat` is not defined. This may be hidden unless compiled for Windows.
- Unix `to_cpath()` does not reject paths containing interior NUL bytes.
- Multiplication may overflow `u64` on unusual platform values.
- The copied sysinfo code has a TODO to replace it with upstream support.

## Test Signals
Tests check that an existing tempdir returns a positive free-space value and a nonexisting path returns `errno` `ENOENT` on supported platforms.
