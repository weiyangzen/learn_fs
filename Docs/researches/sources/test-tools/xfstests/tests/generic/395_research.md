# sources/test-tools/xfstests/tests/generic/395

## Purpose
Test setting and getting encryption policies. It is registered as generic/395 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include empty_dir=$SCRATCH_MNT/empty_dir, nonempty_dir=$SCRATCH_MNT/nonempty_dir, nondirectory=$SCRATCH_MNT/nondirectory, unauthorized_dir=$SCRATCH_MNT/unauthorized_dir. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_encryption; _require_xfs_io_command "get_encpolicy"; _require_user.

External/helper commands: mkdir, mount, touch.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support; depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** Setting encryption policy on empty directory ***; SCRATCH_MNT/empty_dir: failed to get encryption policy: No data available; Encryption policy for SCRATCH_MNT/empty_dir:; 	Policy version: 0; 	Master key descriptor: 0000111122223333; 	Contents encryption mode: 1 (AES-256-XTS). Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
