# sources/test-tools/cthon04/unixdos.h

## Purpose
`unixdos.h` supplies Unix-like typedefs, structs, and function prototypes for DOS/Windows builds of the Connectathon tests. It lets sources using Unix directory, timeval, statfs, and path APIs compile against the legacy DOS compatibility layer.

## Important APIs, Types, and Functions
Important definitions are `struct timeval`, `u_char`, `MAXPATHLEN`, `MIN()`, `fsid_t`, `struct statfs`, dummy `DIR`, simplified `struct dirent`, `MAXNAMLEN`, and `DIRSIZ()`. Declared functions include `gettimeofday()`, `unix_chdir()`, `lstat()`, `statfs()`, `opendir()`, `readdir()`, `rewinddir()`, `closedir()`, `seekdir()`, and `telldir()`.

## Control Flow and State
The header only selects declarations. It avoids redefining `timeval` if Winsock has already supplied one and gates some directory cookie declarations behind `_POSIX_SOURCE`.

## Persistence and Dependencies
No persistent state is created; it defines ABI-compatible shapes that external DOS support code must honor. Dependencies: DOS/Windows compatibility implementations, stat structs from other includes, and tests that include `tests.h` with `DOSorWIN32`.

## Integration Points, Risks, and Test Signals
Integration is the compatibility bridge for non-Unix builds. Risks include intentionally simplified `DIR` and `dirent` structures, `MAXNAMLEN` larger than the actual fixed `d_name[13]`, mismatch with real platform headers, and old-style prototypes. Test signals are successful DOS/Win builds and correct directory/stat behavior in the ported tests.
