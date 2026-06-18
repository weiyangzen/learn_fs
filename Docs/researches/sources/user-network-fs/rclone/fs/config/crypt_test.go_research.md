<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_test.go -->
# sources/user-network-fs/rclone/fs/config/crypt_test.go

## Purpose
External-package tests for encrypted rclone config loading and password-command integration. The file validates the public `config` package behavior against encrypted and malformed fixture files rather than private crypt helpers.

## Important APIs, Types, And Control Flow
Tests exercise `config.SetConfigPath`, `SetConfigPassword`, `IsEncrypted`, `Data().Load`, `ClearConfigPassword`, and `GetPasswordCommand`. The password-command cases mutate `fs.ConfigInfo.PasswordCommand` via context config, then load `testdata/encrypted.conf` with correct and incorrect command output. Failure tests rotate through short, invalid-base64, too-new, and missing config paths.

## State And Persistence
The tests temporarily replace the global config path and global config info, clear the in-memory config password, and restore both in defers. One case writes a temporary Go program to verify that `RCLONE_PASSWORD_CHANGE` is not leaked to direct password-command execution.

## Dependencies And Integration Points
Depends on `fs.GetConfig`, the configfile-backed storage installed elsewhere, encrypted fixture files, `go run` for the environment probe, and testify assertions. It integrates encryption handling with the user-visible config loader.

## Risks And Test Signals
The tests guard wrong passwords, unsupported encryption versions, short payloads, invalid base64, and missing files. Residual risk is that fixture passwords and encrypted blob format are fixed examples, so they do not fuzz all corrupt ciphertext or key-derivation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/crypt_test.go -->
