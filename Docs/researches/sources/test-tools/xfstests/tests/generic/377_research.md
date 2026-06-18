# sources/test-tools/xfstests/tests/generic/377

## Purpose
Test listxattr syscall behaviour with different buffer sizes. It is registered as generic/377 with `_begin_fstest` tags `attr, auto, quick, metadata`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include listxattr=$here/src/listxattr, testfile=${SCRATCH_MNT}/testfile. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_test_program "listxattr".

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, grep, sort, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: xattr: user.foo; xattr: user.hello; xattr: user.ping; listxattr: No such file or directory; listxattr: Numerical result out of range; listxattr: Numerical result out of range. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
