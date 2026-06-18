<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf

## Purpose
Fixture for encrypted config load failure when the encrypted payload contains invalid base64 characters.

## Important APIs, Types, And Control Flow
The file has the encrypted config header and `RCLONE_ENCRYPT_V0:` marker followed by a payload containing non-base64 characters. `crypt_test.go` points `SetConfigPath` at this file and expects `Data().Load()` to return an error.

## State And Persistence
Static test data only. It is never modified by tests.

## Dependencies And Integration Points
Consumed by config encryption tests and the configfile loader's encrypted-file parser.

## Risks And Test Signals
Good regression signal for rejecting corrupt encoded data before decryption. It is a minimal fixture and does not describe every possible malformed encrypted file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/enc-invalid.conf -->
