# sources/test-tools/xfstests/tests/generic/458

## Purpose
Regression test for xfs leftover CoW extents after truncate and umount Fixed by commit 3af423b03435 ("xfs: evict CoW fork extents when performing finsert/fcollapse"). It is registered as generic/458 with `_begin_fstest` tags `auto, quick, clone, collapse, insert, zero`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_xfs_io_command "fzero"; _require_xfs_io_command "fcollapse"; _require_xfs_io_command "finsert"; _require_xfs_io_command "truncate".

External/helper commands: $XFS_IO_PROG, truncate.

Representative `xfs_io` operations: pwrite 0 0x40000; fzero -k 0x169f 0x387c; fcollapse 0x29000 0xd000; finsert 0 0x8000; truncate 0x8000.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
