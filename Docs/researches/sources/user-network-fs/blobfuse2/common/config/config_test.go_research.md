# sources/user-network-fs/blobfuse2/common/config/config_test.go
## sources/user-network-fs/blobfuse2/common/config/config_test.go

Purpose: verifies the configuration parser's unmarshalling, nested-key behavior, env/flag precedence, flag creation helpers, and encrypted config loading.

Important APIs/types: local nested structs `Labels`, `Metadata`, `Selector`, `Template`, `Spec`, `Config1`, `Config2`; fixtures `config1`, `config2`, `metaconf`, `specconf`; and `ConfigTestSuite`.

Control flow: tests load YAML from readers, call `Unmarshal` and `UnmarshalKey` for root and nested subtrees, bind environment variables with `BindEnv`, bind changed pflags with `BindPFlag`, and verify precedence. `TestOverlapShadowConfigReader` demonstrates flags winning over env for the same key while env overrides config for another key. `TestAddFlags` calls all typed flag helper functions and basic setters. `TestConfigFileDecryption` writes a plaintext config, encrypts it with `common.EncryptData`, writes ciphertext, and loads it with `DecryptConfigFile`.

State and persistence: uses global Viper and `userOptions`; cleanup calls `ResetConfig`. Some tests set environment variables but do not explicitly unset them, relying on unique names and later process state not caring. Encryption test writes `test.yaml` and `test_enc.yaml` in the working directory and removes them.

Dependencies/integration: testify, Viper wrapper APIs, pflag, environment variables, filesystem, and AES-GCM utilities.

Risks: `TestAddFlags` passes untyped `5.0` constants to integer helpers; this compiles because constants are representable, but it is visually misleading. Environment variables can leak across tests. The suite does not cover config watchers/listener callbacks or `RegisterFlagCompletionFunc` after `ResetConfig`.

Test signals: strong signal for intended precedence and nested `config` tag mapping.
