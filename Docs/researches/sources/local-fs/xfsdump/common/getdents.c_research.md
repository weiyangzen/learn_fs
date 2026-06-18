# File Research: sources/local-fs/xfsdump/common/getdents.c

## Summary
Wraps the Linux `getdents64` syscall behind a `struct dirent`-oriented interface, based on glibc getdents conversion logic.

## Main Responsibilities
- Define a local `kernel_dirent64` layout matching the Linux syscall record format.
- Optionally allocate a slightly larger temporary buffer if kernel and libc `d_name` offsets differ.
- Call `syscall(SYS_getdents64, ...)`.
- Convert kernel records into libc `struct dirent` records when layouts differ.
- Detect inode/offset overflow and return already converted entries when possible.

## Important Behavior
The conversion logic computes the kernel/libc header-size difference, adjusts record lengths to libc alignment, copies inode/offset/type/name fields, and uses `lseek64()` to roll back to the last safe offset if an overflow occurs after at least one entry.

## Dependencies
Depends on Linux syscall numbers, `dirent`, `alloca`, `offsetof`, `lseek64`, and libc/kernel dirent layout assumptions.

## Risks
The implementation returns immediately when `retval != -1`, which is the successful syscall path. That makes the subsequent conversion loop unreachable on successful reads. If libc `struct dirent` differs from the kernel layout on a target platform, callers may receive unconverted kernel records.

The loop condition after the early return also depends on `retval` being a positive byte count; as written, the only fallthrough path is syscall failure, where `retval == -1`.

The fixed `d_name[256]` in the local kernel struct is a layout stand-in, not a flexible array, so correctness depends on offset and reclen use rather than the declared array capacity.
