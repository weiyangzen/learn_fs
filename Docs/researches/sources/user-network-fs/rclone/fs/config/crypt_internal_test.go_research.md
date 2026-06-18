# sources/user-network-fs/rclone/fs/config/crypt_internal_test.go

Purpose: internal tests for config password hashing/validation and password-change behavior using `--password-command`.

Important APIs/functions: helper `hashedKeyCompare`, `TestPassword`, and `TestChangeConfigPassword`.

Control flow: `TestPassword` clears `configKey` afterward, verifies empty and invalid UTF-8 passwords fail, checks different passwords hash differently, Unicode-normalized equivalents hash the same, and case differences remain distinct. `TestChangeConfigPassword` points config path at an encrypted fixture, writes a temporary Go password-command program that asserts `RCLONE_PASSWORD_CHANGE=1` and prints `asdf`, sets `ci.PasswordCommand`, calls `changeConfigPassword`, then loads config data and verifies decrypted sections/keys.

State and persistence behavior: directly mutates package-global `configKey`, global config path, and `fs.ConfigInfo.PasswordCommand`, restoring them in defers. It verifies password changes affect subsequent config load.

Dependencies and integration points: uses `go run` as a subprocess password command, OS temp files, encrypted testdata, and config storage `Data().Load`.

Risks: the subprocess requires a working Go toolchain in test environment. Global config state must be restored to avoid cross-test contamination.

Test signals: strong coverage for password normalization security expectations and the password-command environment contract during password changes.
