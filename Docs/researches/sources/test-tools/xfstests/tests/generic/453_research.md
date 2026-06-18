# sources/test-tools/xfstests/tests/generic/453

## Purpose
Create a directory with multiple filenames that all appear the same (in unicode, anyway) but point to different inodes. In theory all Linux filesystems should allow this (filenames are a sequence of arbitrary bytes) even if the user implications are horrifying. It is registered as generic/453 with `_begin_fstest` tags `auto, quick, dir`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: hexbytes, setf, setchild, setd, testf, testchild, testd, filter_scrub. Important state variables and paths include testdir=${SCRATCH_MNT}/test-${seq}. Topic focus: filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates byte-distinct pathname fixtures with confusable Unicode renderings; checks stored values, inode uniqueness, and optional xfs_scrub Unicode diagnostics; wraps repeated scenarios in local helper functions hexbytes, setf, setchild, setd, testf, testchild.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch; _require_names_are_bytes.

External/helper commands: grep, ls, mkdir, mount, sed, sort, stat.

## Risks and Edge Cases
depends on byte-oriented pathname handling and locale-safe output filtering.

## Test Signals
The golden `.out` expects normalized signals such as: Format and mount; Create files; Test files; Uniqueness of inodes?; Test XFS online scrub, if applicable. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
