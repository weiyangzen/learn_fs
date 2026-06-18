# sources/test-tools/cthon04/tools/dirdmp.c

## Purpose
dumps raw-ish directory buffer contents by bypassing normal `readdir()` formatting on platforms where `DIR` internals and `getdents`/`getdirentries` are accessible.

## Important APIs, Types, and Functions
`main()`, `print()`, `my_opendir()`, and `my_readdir()` are key; it manipulates `DIR` fields such as `dd_fd`, `dd_buf`, `dd_loc`, `dd_size`, and platform-specific buffer base fields.

## Control Flow and State
For each directory argument, it opens the directory file descriptor, allocates a `DIR`, fills buffers with `getdents` or `getdirentries`, prints location/inode/reclen/name data until EOF, and skips zero-inode entries.

## Persistence and Dependencies
state is allocated directory buffers and file descriptors, released by `closedir()` after printing. Dependencies: private libc `DIR` layout, platform macros for SVR/BSD/SunOS/Mac/OSF1, and low-level directory syscalls.

## Integration Points, Risks, and Test Signals
Integration is diagnostic only. Risks are extreme portability fragility, disabled Linux/AIX support, accessing libc internals, and possible memory leaks on some error paths. Signals are directory entry tables and EOF output.
