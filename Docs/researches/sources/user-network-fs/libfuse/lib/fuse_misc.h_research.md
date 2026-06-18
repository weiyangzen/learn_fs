# sources/user-network-fs/libfuse/lib/fuse_misc.h

Purpose: `fuse_misc.h` centralizes small portability macros used throughout libfuse. It hides platform differences for symbol versioning and nanosecond timestamp fields in `struct stat`.

Important APIs, types, and functions: `FUSE_SYMVER(sym1, sym2)` expands to either a compiler `symver` attribute, an assembler `.symver` directive, or nothing, depending on configuration. Timestamp helpers `ST_ATIM_NSEC`, `ST_CTIM_NSEC`, `ST_MTIM_NSEC` and corresponding setters map to Linux `st_atim`, FreeBSD `st_atimespec`, or no-op/zero fallbacks when nanosecond fields are unavailable.

Control flow: There is no runtime control flow. Preprocessor conditionals choose definitions at compile time from `LIBFUSE_BUILT_WITH_VERSIONED_SYMBOLS`, `HAVE_SYMVER_ATTRIBUTE`, `HAVE_STRUCT_STAT_ST_ATIM`, and `HAVE_STRUCT_STAT_ST_ATIMESPEC`.

State and persistence behavior: The header has no state. The setter macros mutate caller-owned `struct stat` objects when a platform exposes nanosecond fields.

Dependencies and integration points: It includes `pthread.h` and is used by low-level conversion code and helper APIs that need exported ABI symbol names or portable timestamp copying. `fuse_lowlevel.c` relies on these macros when translating between `struct stat` and FUSE wire attributes.

Risks: Macro-only portability code can silently drop timestamp precision on platforms without recognized fields. `FUSE_SYMVER` correctness is build-system and object-format dependent; an incorrect configuration can break ABI compatibility or produce duplicate/missing public symbols.

Test signals: Build tests across Linux, FreeBSD, macOS/no-versioned-symbols, and compilers with and without `symver` attribute are the main signal. Attribute conversion tests should verify nanosecond round-tripping on supported platforms and clean compilation with no-op setters elsewhere.
