# sources/user-network-fs/rclone/fs/config/configfile/configfile_test.go

Purpose: tests configfile storage read/write/reload/save behavior, missing config behavior, symlink handling, and plaintext decrypt handling for non-seekable inputs.

Important APIs/functions: helpers `setConfigFile`, `toUnix`, and `pipedInput`. Tests include `TestConfigFile`, `TestConfigFileReload`, `TestConfigFileDoesNotExist`, `TestConfigFileNoConfig`, `TestConfigFileSave`, `TestConfigFileSaveSymlinkAbsolute`, and `TestPipedConfig`.

Control flow: `TestConfigFile` loads an INI fixture, verifies serialization/sections/keys/values, mutates values, deletes keys/sections, saves, and checks file contents. Reload test appends to the file after load and verifies the next read sees the change. Save tests create nested paths, check directory/file creation, permission preservation, read-only behavior, and expected Linux permission failures. Symlink tests verify saving through absolute and relative symlinks writes the target while preserving the link. Piped config tests ensure `config.Decrypt` can handle non-seekable plaintext without consuming the first line.

State and persistence behavior: tests mutate global config path and real temporary files. They validate temp-file replacement and mode behavior, not just in-memory storage.

Dependencies and integration points: uses `config.SetConfigPath`, `config.Decrypt`, OS filesystem calls, runtime OS checks, and `testify`.

Risks: some tests are platform-gated to Linux because permission semantics differ. Timing-based reload depends on file metadata changes but appending changes both size and content.

Test signals: strong integration coverage for configfile's core persistence guarantees and edge cases.
