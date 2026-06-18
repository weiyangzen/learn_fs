<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config_test.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-config_test.go

Purpose: testify suite for the `gen-config` command's generated YAML shape and required-flag behavior.

Important APIs/types/functions: `genConfig` suite, `SetupTest`, `cleanupTest`, `getDefaultLogLocation`, `executeCommandC`, and tests for file-cache, block-cache, direct-IO, custom output, console output, and missing temp path.

Control flow: each test invokes `rootCmd gen-config` with a particular flag combination, then reads the generated file when one is expected and checks for component names, temp path inclusion, direct-IO setting, and absence of cache path text in direct-IO cases. Cleanup removes `./blobfuse2.yaml` and resets `optsGenCfg`.

State/persistence behavior: writes `./blobfuse2.yaml` or `1.yaml` in the current working directory and removes those files. It creates temporary cache directories for tests that need a path but does not depend on their contents.

Dependencies/integration: depends on component `GenConfig()` output containing strings such as `file_cache` and `block_cache`, the shared command execution helper, and local filesystem write permission.

Risks/test signals: `TestConsoleOutput` asserts the captured command output is empty even though `fmt.Println` writes to process stdout rather than Cobra output, so it is testing the helper's capture behavior as much as command behavior. The suite is narrow but catches regressions in required tmp-path checks, pipeline selection, and file output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config_test.go -->
