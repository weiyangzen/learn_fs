# sources/test-tools/xfstests/tests/generic/415

## Purpose
test for races between write or fpunch operations on reflinked files to read operations on the target file. It is registered as generic/415 with `_begin_fstest` tags `auto, clone, punch`, making it part of the reflink/shared extents, preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include workfile=${SCRATCH_MNT}/workfile, light_clone=${SCRATCH_MNT}/light_clone, file_size=$((10 * 1024 * 1024)), bs=`_get_block_size $SCRATCH_MNT`, block_num=$((file_size / bs)), reflinks_num=20. Topic focus: reflink/shared extents, preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink; _require_xfs_io_command "fpunch"; _require_fs_space $SCRATCH_MNT $((250 * 1024)).

External/helper commands: $XFS_IO_PROG, mount.

Representative `xfs_io` operations: pwrite 0 $file_size; pread $((block_index * bs)) $bs; pwrite $((block_index * bs)) $bs; fpunch $((block_index * bs)) $bs.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
