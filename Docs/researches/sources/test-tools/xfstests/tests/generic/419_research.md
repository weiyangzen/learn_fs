# sources/test-tools/xfstests/tests/generic/419

## Purpose
Try to rename files in an encrypted directory, without access to the encryption key. This should fail with ENOKEY. Test both a regular rename and a cross rename. This is a regression test for: 173b8439e1ba ("ext4: don't allow encrypted operations without keys") 363fa4e078cb ("f2fs: don't allow encrypted operations without keys"). It is registered as generic/419 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include keydesc=$(_generate_session_encryption_key), efile1=$(find $SCRATCH_MNT/edir -maxdepth 1 -type..., efile2=$(find $SCRATCH_MNT/edir -maxdepth 1 -type.... Topic focus: rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble, common/renameat2.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl; _require_renameat2 exchange.

External/helper commands: find, mkdir, mv.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: mv: cannot move 'SCRATCH_MNT/edir/NOKEY_NAME' to 'SCRATCH_MNT/edir/NOKEY_NAME': Required key not available; Required key not available. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
