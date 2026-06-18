# sources/user-network-fs/blobfuse2/cmd/secure_get.go
## sources/user-network-fs/blobfuse2/cmd/secure_get.go

Purpose: implements `blobfuse2 secure get`, which decrypts an encrypted config and prints the requested config key/value.

Important APIs/functions: global `getKeyCmd` with `RunE`; it uses `validateOptions`, `decryptConfigFile(false)`, Viper YAML loading, `viper.Get(secOpts.Key)`, and `reflect.TypeOf` classification.

Control flow: after validation, the command decrypts into memory without saving plaintext. It sets Viper's config type to YAML and reads the plaintext buffer. It then queries `secOpts.Key`. Missing keys return `key not found in config`. Existing values are classified as group-level maps, option-level slices, or scalar values, then printed as `<key> = <value>` to stdout.

State and persistence: reads encrypted config from disk and mutates global Viper state. It does not write files. It uses global `secOpts` populated by persistent secure flags and the `--key` flag.

Dependencies/integration: Cobra, Viper, reflection, string readers, and `secure.go` encryption helpers.

Risks: Viper global state can retain data across command invocations if tests or callers do not reset it. The type classification relies on `reflect.TypeOf(value).String()` prefixes rather than structured type checks. Output goes directly to process stdout rather than Cobra's command output writer, which makes capture less consistent.

Test signals: `secure_test.go` exercises successful scalar retrieval and missing-key error after encrypting a temporary config.
