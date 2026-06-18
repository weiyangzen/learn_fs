# sources/test-tools/xfstests/tests/generic/403

## Purpose
Test racing getxattr requests against large xattr add and remove loop. This reproduces a bug on XFS where a getxattr of an existing attribute spuriously returned failure due to races with attribute fork conversion. It is registered as generic/403 with `_begin_fstest` tags `auto, quick, attr`, making it part of the extended attributes coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include runfile=$tmp.getfattr, getfattr_pid=$!, largeval=`for i in $(seq 0 511); do echo -n a; done`. Topic focus: extended attributes. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs trusted.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, getfattr, rm, touch.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
