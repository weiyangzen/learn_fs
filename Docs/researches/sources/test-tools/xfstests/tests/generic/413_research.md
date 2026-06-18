# sources/test-tools/xfstests/tests/generic/413

## Purpose
mmap direct/buffered io between DAX and non-DAX mountpoints. It is registered as generic/413 with `_begin_fstest` tags `auto, quick, dax, prealloc, mmap`, making it part of the preallocation/range operations coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: prep_files, t_both_dax, t_nondax_to_dax, t_dax_to_nondax, t_both_nondax, t_mmap_dio_dax, do_tests. Important state variables and paths include tsize=$((128 * 1024 * 1024)). Topic focus: preallocation/range operations. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions prep_files, t_both_dax, t_nondax_to_dax, t_dax_to_nondax, t_both_nondax, t_mmap_dio_dax.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_hugepages; _require_test; _require_scratch_dax_mountopt "dax"; _require_test_program "feature"; _require_test_program "t_mmap_dio"; _require_xfs_io_command "falloc".

External/helper commands: $XFS_IO_PROG, grep, mount, rm.

Representative `xfs_io` operations: falloc 0 $tsize.

## Risks and Edge Cases
results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
