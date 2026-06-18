# sources/test-tools/xfstests/tests/generic/447

## Purpose
See how well we handle deleting a file with a million refcount extents. It is registered as generic/447 with `_begin_fstest` tags `auto, clone, punch`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, calc_space. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, fnr=20, free_blocks=$(stat -f -c '%a' "$testdir"), blksz=$(_get_block_size "$testdir"), space_avail=$((free_blocks * blksz)). Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, calc_space.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_test_program "punch-alternating"; _require_xfs_io_command "fpunch".

External/helper commands: $XFS_IO_PROG, attr, mkdir, mount, rm, stat.

Representative `xfs_io` operations: pwrite -S 0x61 -b 4194304 0 $((2 ** (fnr + 1) * blksz)).

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create a many-block file; Reflinking file; Punch file2; Delete file1. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
