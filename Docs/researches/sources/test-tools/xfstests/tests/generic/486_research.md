# sources/test-tools/xfstests/tests/generic/486

## Purpose
Ensure that we can XATTR_REPLACE a tiny attr into a large attr. Kanda Motohiro <kanda.motohiro@gmail.com> reports that XATTR_REPLACE'ing a single-byte attr with a 2048-byte attr causes a fs shutdown because we remove the shortform attr, convert the attr fork to long format, and then try to re-add the attr having not cleared ATTR_REPLACE. Commit 7b38460dc8e4 ("xfs: don't fail when converting shortform attr to long form during ATTR_REPLACE") fixed the xfs bug. It is registered as generic/486 with `_begin_fstest` tags `auto, quick, attr`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, filter_attr_output. Important state variables and paths include max_attr_size=65536. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions _cleanup, filter_attr_output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test_program "attr_replace_test"; _require_attrs; _require_scratch.

External/helper commands: $ATTR_PROG, attr, grep, rm, sed.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Attribute "world" has a NNNN byte value for SCRATCH_MNT/hello. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
