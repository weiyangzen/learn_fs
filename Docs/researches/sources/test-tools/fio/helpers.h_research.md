# sources/test-tools/fio/helpers.h

## Purpose
Declares portability wrappers or fallback definitions for file allocation, sync, and advisory APIs.

## Important APIs, Types, and Functions
Declares `fallocate`, `posix_fallocate`, `sync_file_range`, `syncfs`, and `posix_fadvise` depending on platform feature macros. Includes `sys/types.h` and fio `os/os.h` for `off_t` and `uint64_t` support.

## Control Flow
There is no executable control flow in the header. It ensures callers can reference these functions regardless of platform configuration.

## State and Persistence Behavior
No state is defined.

## Dependencies and Integration Points
Used by helpers implementation and any fio file or I/O path that needs these APIs without direct platform conditionals.

## Risks
Declaring libc-like symbols locally can conflict if feature macros are wrong. The contract depends on configure-time detection being accurate.

## Test Signals
Compile fio on Linux, Windows, and minimal POSIX-like environments with combinations of `CONFIG_SYNC_FILE_RANGE`, `CONFIG_SYNCFS`, and allocation/advice support.
