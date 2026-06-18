# File Research: sources/local-fs/mtd-utils/tests/fs-tests/utils/free_space.c

## Purpose
Prints available filesystem space in bytes.

## Key Elements
Accepts an optional directory argument, handles `--help/-h`, calls `statvfs()`, and prints `f_bavail * f_frsize`.

## Dependencies
Uses standard C and `statvfs`.

## Behavior/Risks
Returns `1` for help and for errors, so help is not a success exit by convention.
