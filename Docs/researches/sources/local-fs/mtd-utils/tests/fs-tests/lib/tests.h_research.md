# File Research: sources/local-fs/mtd-utils/tests/fs-tests/lib/tests.h

## Purpose
Public interface for the shared fs-test support library.

## Key Elements
Defines `CHECK`, default mount directory/type, empty-directory size estimate, helper prototypes for common argument parsing, file creation/checking, fragment/orphan operations, remounting, cleanup, and shared global option variables.

## Dependencies
Includes `stdint.h`; declarations also require POSIX types such as `off_t`, `size_t`, and `pid_t` from including translation units.

## Behavior/Risks
The API exposes global mutable test parameters and flags, so each test program relies on single-process global configuration rather than explicit context objects.
