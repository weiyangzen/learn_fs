# sources/test-tools/xfstests/tests/generic/396

## Purpose
Test that FS_IOC_SET_ENCRYPTION_POLICY correctly validates the fscrypt_policy structure that userspace passes to it. It is registered as generic/396 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include dir=$SCRATCH_MNT/dir. Topic focus: filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption.

External/helper commands: mkdir.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: *** Invalid contents encryption mode ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument; *** Invalid filenames encryption mode ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument; *** Invalid flags ***; SCRATCH_MNT/dir: failed to set encryption policy: Invalid argument. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
