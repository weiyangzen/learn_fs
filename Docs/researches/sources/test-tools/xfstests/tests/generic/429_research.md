# sources/test-tools/xfstests/tests/generic/429

## Purpose
Test that no-key dentries are revalidated after adding a key. Regression test for: 28b4c263961c ("ext4 crypto: revalidate dentry after adding or removing the key") Furthermore, test that no-key dentries are *not* revalidated after "revoking" a key. This used to be done, but it was broken and was removed by: 1b53cf9815bb ("fscrypt: remove broken support for detecting keyring key revocation") Also test for a race condition bug in 28b4c263961c, fixed by: 03a8bb0e53d9 ("ext4/fscrypto: avoid RCU lookup in d_revalidate") Note: the following fix for another race in 28b4c263961c should be applied as well, though we don't test for it because it's very difficult to reproduce: 3d43bcfef5f0 ("ext4 crypto: use dget_parent() in ext4_d_revalidate()"). It is registered as generic/429 with `_begin_fstest` tags `auto, encrypt`, making it part of the encryption, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: show_file_contents, show_directory_with_key. Important state variables and paths include keydesc=$(_generate_key_descriptor), raw_key=$(_generate_raw_encryption_key), nokey_names=( $(find $SCRATCH_MNT/edir -mindepth 1 | s.... Topic focus: encryption, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions show_file_contents, show_directory_with_key.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl; _require_test_program "t_encrypted_d_revalidate".

External/helper commands: find, mkdir, rm, sort.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: ***** Without encryption key *****; --- Directory listing:; SCRATCH_MNT/edir/NOKEY_NAME; SCRATCH_MNT/edir/NOKEY_NAME; --- Contents of files using plaintext names:; cat: SCRATCH_MNT/edir/@@@: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
