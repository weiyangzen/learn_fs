# sources/user-network-fs/blobfuse2/cmd/mountv1_test.go
## sources/user-network-fs/blobfuse2/cmd/mountv1_test.go

Purpose: this is the broad regression suite for the `mountv1` compatibility/conversion command. It verifies that v1-style blobfuse config files and v1 CLI flags are converted into v2 YAML config and component options, and that invalid legacy inputs are rejected with useful errors.

Important APIs and helpers: `generateConfigTestSuite`, `executeCommandC`, `resetCLIFlags`, `randomString`, and `generateFileName` provide isolated Cobra command execution around the global `rootCmd` and global Viper state. Tests unmarshal generated YAML through `common/config` into `azstorage.AzStorageOptions`, `file_cache.FileCacheOptions`, `block_cache.StreamOptions`, `attr_cache.AttrCacheOptions`, `LogOptions`, and `mountOptions`.

Control flow and state: every test creates temporary v1/v2 files, invokes `rootCmd mountv1 --convert-config-only=true`, reads the generated config with Viper, and resets flags plus `viper.Reset()` in cleanup. The cases cover config-file key parsing, SAS/SPN/MSI auth, account type endpoint selection, proxy fields, logging fields, comment stripping, CLI override precedence, file cache and stream component selection, attr cache options, azstorage retry/concurrency fields, libfuse option validation, environment fallback for `AZURE_STORAGE_ACCOUNT`, and invalid account type/name handling.

Dependencies and integration points: the suite depends on Cobra global command registration, Viper global config state, component option structs, temporary filesystem files, and a silent logger. It indirectly exercises `mountv1` parsing/conversion code not in this subset.

Risks: global flags and Viper state make tests order-sensitive if cleanup is missed. The suite asserts generated values but mostly not full YAML shape, so field omissions outside asserted options may escape. Some test names ending in `Error` expect no error for ignored legacy flags, which can confuse maintenance.

Test signals: this file is itself test coverage. It provides strong signal for legacy-to-v2 migration behavior, command-line precedence, invalid FUSE option failures, and environment fallback.
