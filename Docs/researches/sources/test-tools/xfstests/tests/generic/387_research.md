# sources/test-tools/xfstests/tests/generic/387

## Purpose
Create a heavily reflinked file, then check whether we can truncate it correctly. It is registered as generic/387 with `_begin_fstest` tags `auto, clone`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$SCRATCH_MNT/testfile, dummyfile=$SCRATCH_MNT/dummyfile, blocksize=$((128 * 1024)). Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem; forces filesystem writeback/transaction commit; creates shared extents through reflink range cloning; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink.

External/helper commands: $XFS_IO_PROG, dd, rm, truncate.

Representative `xfs_io` operations: truncate 0.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
