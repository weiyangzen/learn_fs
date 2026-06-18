# sources/test-tools/xfstests/tests/generic/401

## Purpose
Test filetype feature This test does NOT require that file system support the d_type feature. It verifies that file types are reported as either DT_UNKNOWN or as the actual file type. For example, special dir entries . and .. MAY be reported as DT_UNKNOWN IF filetype feature is disabled (ext4), but MAY also be reported as DT_DIR in this case (xfs). For fs for which we know how to test the filetype feature (xfs|ext*) verify getting DT_UNKNOWN IFF feature is disabled. It is registered as generic/401 with `_begin_fstest` tags `auto, quick`, making it part of the rename/link persistence, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=$SCRATCH_MNT/find-by-type. Topic focus: rename/link persistence, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_symlinks; _require_mknod; _require_test_program "t_dir_type".

External/helper commands: ln, mkdir, mknod, sort, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: . d; .. d; b b; c c; d d; f f. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
