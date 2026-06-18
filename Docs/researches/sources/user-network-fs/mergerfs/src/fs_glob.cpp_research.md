# sources/user-network-fs/mergerfs/src/fs_glob.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_glob.cpp` expands branch/path glob patterns with `glob(3)`, enabling brace and directory-only matching when the platform supports those flags. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::glob(pattern, vector*)`, `glob`, `glob_t`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::glob(pattern, vector*)` calls `glob`, copies returned paths, and frees `glob_t`; glob errors simply leave the vector unchanged.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_glob.hpp", <glob.h>, <cstdint>, <string>, <vector>. Used by configuration/path parsing code that accepts shell-like branch patterns. Risk is silent empty expansion when `glob` fails or platform flags are compiled to zero.

## Risks and Edge Cases

Used by configuration/path parsing code that accepts shell-like branch patterns. Risk is silent empty expansion when `glob` fails or platform flags are compiled to zero.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
