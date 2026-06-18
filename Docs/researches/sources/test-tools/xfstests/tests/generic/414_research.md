# sources/test-tools/xfstests/tests/generic/414

## Purpose
Check that reflinking adjacent blocks in a file produces a single block mapping extent. It is registered as generic/414 with `_begin_fstest` tags `auto, quick, clone, fiemap, prealloc`, making it part of the reflink/shared extents, preallocation/range operations, fiemap/bmap reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, blocks=32, blksz=65536, sz=$((blocks * blksz)), f1=$(_count_extents $testdir/file1), f2=$(_count_extents $testdir/file2), s1=$($XFS_IO_PROG -c 'fiemap -v' $testdir/fil..., s2=$($XFS_IO_PROG -c 'fiemap -v' $testdir/fil.... Topic focus: reflink/shared extents, preallocation/range operations, fiemap/bmap reporting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; creates shared extents through reflink range cloning; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_xfs_io_command "falloc"; _require_xfs_io_command "fiemap"; _require_congruent_file_oplen $SCRATCH_MNT $blksz.

External/helper commands: $XFS_IO_PROG, awk, grep, md5sum, mkdir, mount, rm.

Representative `xfs_io` operations: falloc 0 $sz; fiemap -v; 0x.*[2367aAbBfF]...$.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create the original files; Compare files; de89461b64701958984c95d1bfb0065a  SCRATCH_MNT/test-414/file1; de89461b64701958984c95d1bfb0065a  SCRATCH_MNT/test-414/file2; Check extent counts. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
