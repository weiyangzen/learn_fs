# File Research: sources/local-fs/xfsprogs/db/fuzz.h

## Purpose
Declares xfs_db fuzzing entry points.

## Interfaces
- `fuzz_init()` registers the expert-mode command.
- `fuzz_struct()` is the field-structure pfunc path used to fuzz parsed fields.
