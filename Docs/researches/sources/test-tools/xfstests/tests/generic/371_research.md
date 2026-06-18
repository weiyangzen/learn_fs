# sources/test-tools/xfstests/tests/generic/371

## Purpose
Run write(2) and fallocate(2) in parallel and the total needed data space for these operations don't exceed whole fs free data space, to see whether we will get any unexpected ENOSPC error. It is registered as generic/371 with `_begin_fstest` tags `auto, quick, enospc, prealloc`, making it part of the preallocation/range operations, ENOSPC/free-space handling coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile1=$SCRATCH_MNT/testfile1, testfile2=$SCRATCH_MNT/testfile2. Topic focus: preallocation/range operations, ENOSPC/free-space handling. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "falloc"; test "$FSTYP" = "xfs" && _require_xfs_io_command "extsize".

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: extsize $alloc_sz.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
