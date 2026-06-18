<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint_test.go -->
# sources/user-network-fs/rclone/fs/fingerprint_test.go

## Purpose
Tests object fingerprint composition under fast/slow feature combinations.

## Important APIs, Types, And Control Flow
Creates a mock Fs with MD5 support and a mock object containing `data`, toggles `Features().SlowModTime` and `SlowHash`, and asserts exact fingerprint strings for fast and non-fast calls.

## State And Persistence
Local mock state only.

## Dependencies And Integration Points
Uses `fstest/mockfs`, `mockobject`, and hash registry support.

## Risks And Test Signals
Good coverage of feature gating. It does not test unsupported modtime precision, hash errors, or a backend with no hashes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fingerprint_test.go -->
