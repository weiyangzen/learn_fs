# sources/test-tools/xfstests/tests/generic/473

## Purpose
Test for the new ranged query functionality in xfs_io's fiemap command. This tests various combinations of hole + data layout being printed. Also the test used 16k holes to be compatible with 16k block filesystems. It is registered as generic/473 with `_begin_fstest` tags `broken, fiemap`, making it part of the fiemap/bmap reporting, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include file=$TEST_DIR/fiemap.$seq. Topic focus: fiemap/bmap reporting, holes/sparse files. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/punch.

Prerequisite gates: _require_test; _require_xfs_io_command "truncate"; _require_xfs_io_command "fiemap" "ranged".

External/helper commands: $XFS_IO_PROG, rm, truncate.

Representative `xfs_io` operations: truncate 4m; pwrite $(($i*128+64))k 64k; fiemap -v 64k 64k; fiemap -v 64k 80k; fiemap -v 0 65k; fiemap -v 0k 130k; fiemap -v 64k 192k; fiemap -v 0 3k; fiemap -v 0 3m; fiemap -v 0 5m.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Basic data extent; 0: [128..255]: data; Data + Hole; 0: [128..255]: data; 1: [256..287]: hole; Hole + Data. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
