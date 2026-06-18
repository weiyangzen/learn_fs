# sources/test-tools/xfstests/tests/generic/421

## Purpose
Test revoking an encryption key during concurrent I/O. Regression test for 1b53cf9815bb ("fscrypt: remove broken support for detecting keyring key revocation"). It is registered as generic/421 with `_begin_fstest` tags `auto, quick, encrypt, dangerous`, making it part of the encryption, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include dir=$SCRATCH_MNT/encrypted_dir, file=$dir/file, nproc=4, slice=2, keydesc=$(_generate_session_encryption_key), keyid=$(_revoke_session_encryption_key $keydesc). Topic focus: encryption, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; forces durability boundaries with sync/fsync operations.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_command "$KEYCTL_PROG" keyctl.

External/helper commands: $XFS_IO_PROG, find, mkdir, rm, touch.

Representative `xfs_io` operations: pwrite 0 $((nproc*slice))M; fsync; fadvise -d $range; pread $range.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior; requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: Didn't crash!. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
