# sources/storage-engines/tikv/components/tikv_alloc/src/error.rs

## Purpose
This file defines the error type used by allocator profiling and control APIs.

## Important APIs, Types, and Control Flow
`ProfError` distinguishes disabled profiling, I/O errors, jemalloc control errors, non-Unicode dump paths, and paths containing NUL bytes. `ProfResult<T>` is the crate-local result alias. `Display` formats user-facing messages, and `From<std::io::Error>` plus `From<std::ffi::NulError>` make filesystem and CString conversion failures flow into allocator APIs.

## State, Dependencies, and Integration
The type is stateless and shared by `default.rs`, `jemalloc.rs`, and public callers through `tikv_alloc::error`. Profiling dump code uses it when converting paths and when jemalloc mallctl calls fail.

## Risks and Test Signals
The error messages are simple and not structured with source chains beyond implementing `std::error::Error`. Consumers that need exact jemalloc failure classes only receive strings. Tests are indirect through profiling tests and no-op backend behavior.
