<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go -->
# sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go

Purpose: tests for ADLS Gen1 JSON generation and mountgen1 error handling.

Important APIs/types/functions: `genOneConfigTestSuite`, fixtures `configGenOne`, `invalidConfig`, `invalidAuthMode`, `executeCommandC`, `config.ReadFromConfigFile`, `config.UnmarshalKey`, `viper.SetConfigFile`, and `resetCLIFlags`.

Control flow: setup installs a silent logger. `TestConfigCreation` writes a full SPN config, runs `mountgen1` with `--generate-json-only`, reads the output JSON through the config layer, and verifies client ID, tenant ID, cache dir, and mount dir. Negative tests write configs missing required fields or using auth mode `key` and expect errors. `TestGen1FuseMount` omits generate-only and expects failure because the external `adlsgen1fuse` binary is not available or cannot mount in the test environment.

State/persistence behavior: creates temp config files, temp JSON output files, and temp mount directories, removes them after each test, and resets `generateJsonOnly` and CLI flags.

Dependencies/integration: depends on config parser support for JSON after generation, command helper execution, and mountgen1's global state. The suite intentionally avoids persisting secrets; client secret is not checked.

Risks/test signals: `viper.SetConfigFile("json")` is unusual global state and can leak if not reset elsewhere. Assertions cover a representative subset of JSON fields, not the entire generated schema. The external-binary failure test could change if `adlsgen1fuse` is installed and runnable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go -->
