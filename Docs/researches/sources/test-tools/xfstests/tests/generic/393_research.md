# sources/test-tools/xfstests/tests/generic/393

## Purpose
Test some small truncations to check inline_data and its cached data are truncated correctly at the same time. The inline_data feature was introduced in ext4 and f2fs as follows. ext4 : http://lwn.net/Articles/468678/ f2fs : http://lwn.net/Articles/573408/ The basic idea is embedding small-sized file's data into relatively large inode space. In ext4, up to 132 bytes of data can be stored in 256 bytes-sized inode. In f2fs, up to 3.4KB of data can be embedded into 4KB-sized inode block. It is registered as generic/393 with `_begin_fstest` tags `auto, quick, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$SCRATCH_MNT/testfile, OD_CMD=od -A x -t x1z. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: pwrite -S 0x58 0 40; fsync; truncate 0; truncate 50; truncate 4096; truncate 4.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 40/40 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); = truncate inline_data after #0 page was truncated entirely =; 000000 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  >................<; *; 000030 00 00                                            >..<. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
