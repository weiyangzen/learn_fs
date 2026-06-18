<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc_test.go -->
# sources/user-network-fs/blobfuse2/cmd/doc_test.go

Purpose: testify suite validating the hidden `doc` command's filesystem handling and Markdown generation error paths.

Important APIs/types/functions: `docTestSuite`, `SetupTest`, `cleanupTest`, `executeCommandC`, `resetCLIFlags`, `randomString`, `os.ReadDir`, `os.CreateTemp`, and tests `TestDocsGeneration`, `TestOutputDirCreationError`, `TestDocsGenerationError`, and `TestOutputDirIsFileError`.

Control flow: setup resets `docCmdInput` and mount options, installs a silent logger, and each test invokes the Cobra command through `executeCommandC`. The success case creates a temp output directory under `/tmp`, runs `doc`, and asserts files exist. Negative cases use unwritable or invalid paths and assert returned output contains expected error fragments.

State/persistence behavior: creates temporary directories and files, removes them with defers, and resets CLI flags after tests to avoid cross-test Cobra state leakage.

Dependencies/integration: depends on root command registration, Cobra doc generation, test helper `executeCommandC`, and filesystem permissions that make `/var/docs_*` unwritable in normal test environments.

Risks/test signals: tests assert error text fragments, so wording changes can break them. Running as root may alter permission assumptions for `/var/docs_*`. The suite's main signal is command behavior before and during Markdown tree generation rather than content correctness of generated docs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc_test.go -->
