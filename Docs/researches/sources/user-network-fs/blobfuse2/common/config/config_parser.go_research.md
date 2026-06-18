# sources/user-network-fs/blobfuse2/common/config/config_parser.go
## sources/user-network-fs/blobfuse2/common/config/config_parser.go

Purpose: central configuration wrapper around Viper that enforces blobfuse precedence: flags, environment variables, then config file.

Important APIs/types/functions: `ConfigChangeEventHandler`, `ConfigChangeEventHandlerFunc`, `KeysTree`, internal `options`/`userOptions`, `SetSecureConfigOptions`, `SetConfigFile`, `ReadFromConfigFile`, `ReadFromConfigBuffer`, `DecryptConfigFile`, `WatchConfig`, `ReadConfigFromReader`, `AddConfigChangeEventListener`, `BindEnv`, `BindPFlag`, `UnmarshalKey`, `Unmarshal`, `Set`, `SetBool`, `IsSet`, flag creation helpers, `RegisterFlagCompletionFunc`, and `ResetConfig`.

Control flow: config files or buffers are loaded into global Viper, then `WatchConfig` installs an fsnotify callback. `Unmarshal`/`UnmarshalKey` first decode Viper data with the `config` struct tag, then overlay environment values from `envTree`, then changed flags from `flagTree`. Secure configs are decrypted on file-change events before notifying listeners. Flag helpers add options to a shared pflag set that can be attached to Cobra commands.

State and persistence: `userOptions` and Viper are global mutable state. `DecryptConfigFile` reads encrypted files and loads plaintext into Viper but does not write. Watchers/listeners persist for process lifetime unless `ResetConfig` is called.

Dependencies/integration: Viper, pflag, Cobra completions, fsnotify, mapstructure, `common.EncryptData`/`DecryptData`, and `common/log`.

Risks: `IsSet` walks `flagTree` and assumes the final node value is a `*pflag.Flag`, which can panic for malformed intermediate state. `ResetConfig` omits reinitializing `completionFuncMap`, unlike `init`, so registering completions after reset can panic unless another initializer restores it. Viper global state and watchers make tests and command reuse sensitive to cleanup.

Test signals: `config_test.go` covers config-only decode, env shadowing, flag shadowing, flag-over-env precedence, flag helper creation, and encrypted config loading.
