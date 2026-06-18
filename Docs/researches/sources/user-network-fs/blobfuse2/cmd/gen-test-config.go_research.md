<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-test-config.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-test-config.go

Purpose: hidden test helper command that expands template config files by replacing placeholders with environment values, a container name, and a temp path.

Important APIs/types/functions: `configGenOptions`, global `opts`, `templatesDir`, hidden Cobra command `generateTestConfig`, `os.ReadFile`, regexp `{.*?}`, `os.Getenv`, and `os.WriteFile`.

Control flow: read the template either from the provided path when it already contains `testdata/config/` or from `testdata/config/<config-file>`. Find every `{ ... }` token. Replace `{ 0 }` with `--container-name`, `{ 1 }` with `--temp-path`, and all other tokens with the environment variable whose name is inside the braces. Write the expanded config to `--output-file` with mode `0700`.

State/persistence behavior: creates or overwrites the output config file. It reads process environment variables but does not validate that replacements are non-empty. It stores command options in package-global `opts`.

Dependencies/integration: used by tests and automation that need runtime credentials or temp paths injected into config templates. It depends on the template placeholder format with spaces inside braces.

Risks/test signals: regexp replacement treats placeholders as regular expressions and can behave unexpectedly if placeholder contents gain regex metacharacters. Missing flags are not explicitly validated, and empty environment variables silently become empty config values. No direct test file is included in this work item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-test-config.go -->
