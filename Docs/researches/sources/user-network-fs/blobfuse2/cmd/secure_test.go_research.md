# sources/user-network-fs/blobfuse2/cmd/secure_test.go
## sources/user-network-fs/blobfuse2/cmd/secure_test.go

Purpose: provides regression coverage for secure config command registration and encryption/decryption/get/set behavior.

Important APIs/helpers: `secureConfigTestSuite`, `executeCommandSecure`, `resetSecureCLIFlags`, `testPlainTextConfig`, and `TestSecureConfig`. Tests invoke the real global `rootCmd` with secure subcommands and temporary files.

Control flow: setup installs a silent logger. Tests cover help, encrypting to a provided output file, nonexistent config, missing config, missing passphrase, invalid AES key length, decrypting a previously encrypted config to `./tmp.yaml`, getting an existing key, getting an invalid key, and setting `logging.level` before getting it again. Temporary config files are removed with defers.

State and persistence: tests write plaintext and encrypted temporary files and one fixed `./tmp.yaml` file. They mutate global Cobra command args/outputs and secure flags. Cleanup currently resets `generateConfigCmd` flags, which appears unrelated to secure flags and may leave some secure flag state to Cobra's own test execution behavior.

Dependencies/integration: uses actual `common.EncryptData`/`DecryptData`, filesystem temp files, Cobra command execution, and global Viper behavior inside secure get/set.

Risks: fixed `./tmp.yaml` can collide if tests run concurrently or fail before cleanup. The flag reset helper targets `generateConfigCmd`, not `secureCmd`/subcommands, which is a maintainability hazard. Output from `secure get/set` uses stdout, but tests mostly assert only error/no-error rather than exact output or final decrypted value.

Test signals: confirms valid AES key length, passphrase requirement, round-trip byte equality for decrypt, and scalar update command path.
