# sources/test-tools/xfstests/tests/generic/452

## Purpose
This is a regression test for kernel patch: commit fd96b8da68d3 ("ext4: fix fault handling when mounted with -o dax,ro") created by Ross Zwisler <ross.zwisler@linux.intel.com>. It is registered as generic/452 with `_begin_fstest` tags `auto, quick, dax`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include LS=$(type -P ls), SCRATCH_LS=$SCRATCH_MNT/ls_on_scratch. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch.

External/helper commands: cp, ls.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: SCRATCH_MNT/ls_on_scratch; SCRATCH_MNT/ls_on_scratch. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
