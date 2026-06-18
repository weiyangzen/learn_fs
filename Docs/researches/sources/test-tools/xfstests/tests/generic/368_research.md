# sources/test-tools/xfstests/tests/generic/368

## Purpose
Verify the ciphertext for encryption policies that use a hardware-wrapped inline encryption key, the IV_INO_LBLK_64 flag, and AES-256-XTS. It is registered as generic/368 with `_begin_fstest` tags `auto, quick, encrypt`, making it part of the encryption coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: encryption. Key helper behavior includes: requires inline encryption support; verifies fscrypt ciphertext for a policy.

## Control Flow
runs a direct harness scenario and compares stdout to the golden output.

## State and Persistence Behavior
relies on the xfstests harness cleanup path and golden-output comparison.

## Dependencies and Integration Points
Common libraries: common/encrypt, common/filter, common/preamble.

Prerequisite gates: _require_scratch_inlinecrypt.

## Risks and Edge Cases
requires compatible fscrypt, inline encryption, and hardware-wrapped key support.

## Test Signals
The golden `.out` expects normalized signals such as: Verifying ciphertext with parameters:; 	contents_encryption_mode: AES-256-XTS; 	filenames_encryption_mode: AES-256-CTS-CBC; 	options: v2 iv_ino_lblk_64 hw_wrapped_key. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
