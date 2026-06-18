# sources/test-tools/xfstests/tests/generic/412

## Purpose
Test that if we have a file with a hole, do a mix of direct IO and buffered writes to it and truncate the file to a size that lies in the middle of the hole, after unmounting and mounting again the filesystem, the file has a correct size and no data loss happened. It is registered as generic/412 with `_begin_fstest` tags `auto, quick, metadata`, making it part of the holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: holes/sparse files. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_odirect.

External/helper commands: $XFS_IO_PROG, md5sum, truncate.

Representative `xfs_io` operations: pwrite -S 0x01 0K 32K; pwrite -S 0x02 -b 32K 64K 32K; truncate 60K.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 32768/32768 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); wrote 32768/32768 bytes at offset 65536; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); File digest before unmounting the filesystem:; 3c5ca3c3ab42f4b04d7e7eb0b0d4d806  SCRATCH_MNT/foo. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
