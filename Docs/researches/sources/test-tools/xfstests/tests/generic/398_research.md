# sources/test-tools/xfstests/tests/generic/398

## Purpose
Filesystem encryption is designed to enforce that a consistent encryption policy is used within a given encrypted directory tree and that an encrypted directory tree does not contain any unencrypted files. This test verifies that filesystem operations that would violate this constraint fail. This does not test enforcement of this constraint on lookup, which is still needed to detect offline changes. It is registered as generic/398 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include edir1=$SCRATCH_MNT/edir1, edir2=$SCRATCH_MNT/edir2, udir=$SCRATCH_MNT/udir, keydesc1=$(_generate_session_encryption_key), keydesc2=$(_generate_session_encryption_key), efile1=$(find $edir1 -type f), efile2=$(find $edir2 -type f). Topic focus: rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble, common/renameat2.

Prerequisite gates: _require_scratch_encryption; _require_renameat2 exchange.

External/helper commands: find, ln, mkdir, mkfifo, rm, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: *** Link encrypted <= encrypted ***; ln: failed to create hard link 'SCRATCH_MNT/edir2/efile1' => 'SCRATCH_MNT/edir1/efile1': Invalid cross-device link; *** Rename encrypted => encrypted ***; Invalid cross-device link; *** Link unencrypted <= encrypted ***; ln: failed to create hard link 'SCRATCH_MNT/edir1/ufile' => 'SCRATCH_MNT/udir/ufile': Invalid cross.... Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
