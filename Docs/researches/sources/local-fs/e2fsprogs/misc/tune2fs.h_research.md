# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.h

## Purpose
Small public header for embedding tune2fs behavior as a library entry point.

## Key Elements
Defines an include guard and C++ linkage wrapper. Declares `int tune2fs_main(int argc, char **argv);`, documented as taking the same arguments as the `tune2fs` executable and serving as the `libtune2fs` entry point.

## Dependencies
No external headers are included. Consumers are expected to provide normal C runtime argument arrays.

## Behavior/Risks
The header exposes the whole command-line tool as a callable API rather than a structured library interface, so callers inherit process-oriented behavior from `tune2fs.c`, including global option state, output to stdio/stderr, and exit-like error paths depending on build mode.
