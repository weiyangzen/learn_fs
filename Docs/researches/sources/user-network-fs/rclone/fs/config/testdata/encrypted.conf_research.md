<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf -->
# sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf

## Purpose
Known-good encrypted config fixture used to validate password-based and password-command-based config loading.

## Important APIs, Types, And Control Flow
The fixture has the encrypted config header, `RCLONE_ENCRYPT_V0:` marker, and a payload that decrypts with password `asdf` into remotes `nounc` and `unc`.

## State And Persistence
Static test data. Tests read it repeatedly and clear the process config password afterward.

## Dependencies And Integration Points
Used by `crypt_test.go` with both direct `SetConfigPassword` and `PasswordCommand` flows.

## Risks And Test Signals
It is the main positive signal for encrypted config compatibility. Since it is a single encrypted blob, it does not exercise large configs, many sections, or alternate password encodings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/testdata/encrypted.conf -->
