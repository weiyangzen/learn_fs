# sources/distributed-fs/tahoe-lafs/src/allmydata/test/mutable/test_update.py

## Purpose
This file tests ranged update behavior for mutable files, especially MDMF files with multiple segments and SDMF files with a single segment. It focuses on append, replace, zero-length writes, segment-boundary fenceposts, file extension, last-segment replacement, and reencoding when segment counts cross a power-of-two boundary.

## Important APIs, Types, And Functions
`Update` combines `GridTestMixin`, `AsyncTestCase`, and `ShouldFailMixin`. Key helpers are `do_upload_sdmf`, `do_upload_mdmf`, `_test_replace`, and `_check_differences`. The tests use `MutableFileNode`, `MutableData`, `MDMF_VERSION`, `DEFAULT_MUTABLE_MAX_SEGMENT_SIZE`, and a local `SEGSIZE` constant matching the historical 128 KiB assumption.

## Control Flow
`setUp` creates a no-network grid with 13 servers, stores the first client and nodemaker, and prepares a multi-segment byte string plus a small SDMF payload. Each update test uploads a mutable file, gets its best mutable version, invokes `mv.update(MutableData(new_data), offset)`, downloads the best version, and compares exact bytes. The location test iterates over offsets near one- and two-segment boundaries and applies sequential two-byte replacements.

## State, Persistence, And Dependencies
Unlike `mutable/util.py`, this test uses the full no-network grid and real share files on disk under a temporary basedir. It relies on default encoding/segment-size behavior and directly writes `EXPECTED` and `GOT` diagnostic files if a large-data comparison fails.

## Risks And Test Signals
The primary risk covered is data corruption around segment slicing and mutable update reencoding. The file is deliberately coupled to segment size, and comments call this out as a cleanup target. It also catches regressions where SDMF update support diverges from MDMF update behavior.
