# sources/test-tools/xfstests/tests/generic/440

## Purpose
Test that when the filesystem tries to enforce that all files in a directory tree use the same encryption policy, it doesn't get confused and incorrectly return EPERM in cases where the parent's key is cached but not the child's, or vice versa. Such situations can arise following removal of the master key from the keyring. Regression test for: 272f98f68462 ("fscrypt: fix context consistency check when key(s) unavailable"). It is registered as generic/440 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the encryption, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_key_descriptor), raw_key=$(_generate_raw_encryption_key). Topic focus: encryption, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_symlinks; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: find, ln, ls, mkdir, sort, stat.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: ***** Parent has key, but child doesn't *****; file; subdir; symlink; cat: SCRATCH_MNT/edir/file: Required key not available; cat: SCRATCH_MNT/edir/symlink: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
