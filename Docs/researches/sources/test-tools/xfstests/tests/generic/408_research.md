# sources/test-tools/xfstests/tests/generic/408

## Purpose
Verify that mtime is not updated when deduping files. It is registered as generic/408 with `_begin_fstest` tags `auto, quick, clone, dedupe, metadata`, making it part of the reflink/shared extents, dedupe coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include sourcefile=$TEST_DIR/dedup_mtime_sourcefile, destfile=$TEST_DIR/dedup_mtime_destfile, mtime1=`stat -c %Y $destfile`, ctime1=`stat -c %Z $destfile`, mtime2=`stat -c %Y $destfile`, ctime2=`stat -c %Z $destfile`. Topic focus: reflink/shared extents, dedupe. Key helper behavior includes: deduplicates matching byte ranges.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
uses persistent files under TEST_DIR; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_test; _require_test_dedupe.

External/helper commands: $XFS_IO_PROG, rm, stat.

Representative `xfs_io` operations: pwrite 0 4k.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
