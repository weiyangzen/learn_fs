<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf

## Purpose
Fixture for encrypted config load failure when the payload is too short to contain required encryption metadata/ciphertext.

## Important APIs, Types, And Control Flow
The file uses the encrypted config header and `RCLONE_ENCRYPT_V0:` marker with a truncated base64-looking payload. The config load test expects an error when decoding/decrypting it.

## State And Persistence
Static immutable test data.

## Dependencies And Integration Points
Used by `TestConfigLoadEncryptedFailures` in the external config tests.

## Risks And Test Signals
Confirms short encrypted files do not silently load as empty configs. It does not cover all boundary lengths around the minimum encrypted payload size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-short.conf -->
