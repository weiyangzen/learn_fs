<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/generator.go -->
# sources/user-network-fs/blobfuse2/cmd/generator.go

Purpose: hidden Cobra command that exposes the component generator script through the Blobfuse2 CLI for developer use.

Important APIs/types/functions: hidden `generateCmd`, `cobra.ExactArgs(1)`, `exec.Command("./cmd/componentGenerator.sh", componentName)`, and stdout/stderr forwarding to the current process.

Control flow: accept one component name, run `./cmd/componentGenerator.sh <component>`, mirror script output to stdout, and return a wrapped error if the script exits unsuccessfully.

State/persistence behavior: the Go file itself only starts a subprocess, but the subprocess creates component files and rewrites `cmd/imports.go`. No state cleanup or transactionality is provided if generation is partial.

Dependencies/integration: depends on repository-root current working directory, executable shell scripts, and the template/import generator contract. It is integrated into the root Cobra command but hidden from normal users.

Risks/test signals: running from a different working directory fails because the script path is relative. There is no validation of component name before shelling out. No tests are included here; compile-time command registration and successful subprocess execution are the available signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/generator.go -->
