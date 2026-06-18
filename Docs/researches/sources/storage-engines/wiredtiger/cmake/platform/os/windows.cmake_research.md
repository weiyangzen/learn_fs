# sources/storage-engines/wiredtiger/cmake/platform/os/windows.cmake

## Purpose
`windows.cmake` applies Windows/MSVC-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX OFF`, forces `SPINLOCK_TYPE=msvc`, enables static and disables shared builds, enables PIC, adds MSVC compile options, constructs `win_link_flags`, and appends them to `CMAKE_EXE_LINKER_FLAGS`.

## Control Flow
There is no branching. All Windows builds receive static-library defaults and MSVC warning/optimization/linker compatibility flags.

## State And Persistence Behavior
It mutates cache values and global compile/link flags. These settings persist in the CMake build directory and influence target creation in `define_libwiredtiger.cmake`.

## Dependencies And Integration Points
It integrates with `base.cmake` Windows CRT selection, spinlock configuration, and generated config headers. The forced static build supports producing a `.lib`; shared DLL production is expected through additional DEF-file handling elsewhere.

## Risks
Forcing shared off can surprise users expecting DLL builds. Flags are MSVC-specific and unsuitable for non-MSVC Windows toolchains unless guarded by upstream platform selection. Global warning suppressions can hide portability issues.

## Test Signals
Configure Windows/MSVC builds; verify static target generation, spinlock macro, runtime library selection, and linker flags `/DYNAMICBASE` and `/NXCOMPAT`.
