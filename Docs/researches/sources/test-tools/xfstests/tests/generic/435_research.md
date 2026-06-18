# sources/test-tools/xfstests/tests/generic/435

## Purpose
Test that without the encryption key for a directory, long filenames are presented in a way which avoids collisions, even though they are abbreviated in order to support names up to NAME_MAX bytes. Regression test for: 6332cd32c829 ("f2fs: check entire encrypted bigname when finding a dentry") 6b06cdee81d6 ("fscrypt: avoid collisions when presenting long encrypted filenames") Even with these two fixes it's still possible to create intentional collisions. For now this test covers "accidental" collisions only. It is registered as generic/435 with `_begin_fstest` tags `auto, encrypt`, making it part of the encryption coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key). Topic focus: encryption. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: find, mkdir, rm, sort, stat, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: 100000; 100000; stat: cannot statx 'SCRATCH_MNT/edir': No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
