# sources/test-tools/xfstests/tests/generic/373

## Purpose
Check that cross-mountpoint reflink works. It is registered as generic/373 with `_begin_fstest` tags `auto, quick, clone`, making it part of the reflink/shared extents coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_otherdir. Important state variables and paths include testdir=$SCRATCH_MNT/test-$seq, otherdir=$tmp.m.$seq, othertestdir=$otherdir/test-$seq, blocks=1, blksz=65536, sz=$((blksz * blocks)). Topic focus: reflink/shared extents. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; writes deterministic byte patterns; requires reflink support on scratch.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; exercises clone/dedupe shared-extent operations; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_otherdir.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; depends on extent layout and size metadata remaining consistent.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/reflink.

Prerequisite gates: _require_scratch_reflink; _require_cp_reflink.

External/helper commands: $MOUNT_PROG, md5sum, mkdir, mount, rm, sed.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; results are sensitive to filesystem feature support and allocation alignment.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Mount otherdir; Create file; Reflink one file to another; Check output; 2d61aa54b58c2e94403fb092c3dbc027  SCRATCH_MNT/test-373/file. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
