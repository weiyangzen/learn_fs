# sources/test-tools/xfstests/tests/generic/454

## Purpose
Create xattrs with multiple keys that all appear the same (in unicode, anyway) but point to different values. In theory all Linux filesystems should allow this (filenames are a sequence of arbitrary bytes) even if the user implications are horrifying. It is registered as generic/454 with `_begin_fstest` tags `auto, quick, attr`, making it part of the preallocation/range operations, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: hexbytes, setf, testf, filter_scrub. Important state variables and paths include testdir=${SCRATCH_MNT}/test-${seq}, testfile=${testdir}/attrfile, crazy_keys=$(_getfattr --absolute-names -d "${testfil..., expected_keys=11. Topic focus: preallocation/range operations, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions hexbytes, setf, testf, filter_scrub.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; persists extended-attribute namespace/value state.

## Dependencies and Integration Points
Common libraries: common/attr, common/preamble.

Prerequisite gates: _require_scratch; _require_attrs; _require_names_are_bytes.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, attr, grep, mkdir, mount, sed, touch.

## Risks and Edge Cases
depends on byte-oriented pathname handling and locale-safe output filtering.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create files; Test files; Uniqueness of keys?; Test XFS online scrub, if applicable. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
