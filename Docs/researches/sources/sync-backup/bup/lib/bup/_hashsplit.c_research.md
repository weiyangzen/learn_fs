# sources/sync-backup/bup/lib/bup/_hashsplit.c

## Purpose
C implementation of bup's content-defined splitting Python extension types. It provides streaming file splitting and record-oriented split decisions using the rolling checksum from `bupsplit.h`.

## Important APIs, Types, and Functions
Defines Python types `_helpers.HashSplitter` and `_helpers.RecordHashSplitter`; initialization function `hashsplit_init`; helpers `HashSplitter_nextfile`, `HashSplitter_read`, `HashSplitter_roll`, `HashSplitter_iternext`, `RecordHashSplitter_feed`, and optional `HashSplitter_uncache`.

## Control Flow
`HashSplitter` iterates input files, reads fd or `.read()` data into an advice-sized buffer, finds rolling checksum boundaries, forces max-blob splits, optionally keeps file boundaries, and returns `(memoryview_slice, level)`. `RecordHashSplitter.feed` rolls through a supplied record and returns `(split, bits)` while resetting after split or max size.

## State and Persistence Behavior
State is in C structs: file iterator/current object, fd, buffer start/end, EOF, rollsum, split sizes, fanbits, progress callback, and optional mincore page cache tracking. It does not persist files but can issue `POSIX_FADV_DONTNEED`.

## Dependencies and Integration Points
Depends on generated config, Python C API, OS fd/read/mmap/mincore/fadvise support, `bup/intprops.h`, `bup/pyutil.h`, and `bupsplit.h`. Registered by `_helpers.c`.

## Risks and Test Signals
Risks include overflow, buffer lifetime via memoryviews, fd vs Python read behavior, page-cache advice correctness, and split boundary regressions. Signals are deterministic chunk boundaries, max-blob enforcement, progress callbacks, overflow exceptions, and rollsum selftests.
