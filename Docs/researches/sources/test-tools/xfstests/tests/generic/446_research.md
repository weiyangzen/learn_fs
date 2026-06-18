# sources/test-tools/xfstests/tests/generic/446

## Purpose
Regression test for commit: 04197b3 ("xfs: don't BUG() on mixed direct and mapped I/O") This case tests a race between a direct I/O read and a mapped write to a hole in a file. On xfs filesystem, it will trigger a BUG_ON(). It is registered as generic/446 with `_begin_fstest` tags `auto, quick, rw, punch, mmap`, making it part of the preallocation/range operations, holes/sparse files coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include filesz=$((65536 * 2)), dread_pid=$!. Topic focus: preallocation/range operations, holes/sparse files. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_xfs_io_command "truncate"; _require_xfs_io_command "fpunch"; _require_odirect.

External/helper commands: $XFS_IO_PROG, truncate.

Representative `xfs_io` operations: truncate $((filesz * 2)); pread 0 $filesz; mmap 0 $filesz; mwrite 0 $filesz; fpunch 0 $filesz.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
