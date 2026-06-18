<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc.go -->
# sources/user-network-fs/blobfuse2/cmd/doc.go

Purpose: hidden Cobra command that generates Markdown documentation for the complete Blobfuse2 command tree.

Important APIs/types/functions: `docCmdInput.outputLocation`, hidden `docCmd`, `os.Stat`, `os.MkdirAll`, `cobra/doc.GenMarkdownTree`, and `rootCmd.AddCommand(docCmd)`. The `--output-location` persistent flag defaults to `./doc`.

Control flow: `RunE` validates the output path. If the path is absent it creates the directory, if it is inaccessible it returns a wrapped access error, and if it is a file it rejects it. After validation it calls `doc.GenMarkdownTree(rootCmd, outputLocation)` and returns a user-facing error if generation fails.

State/persistence behavior: creates or populates the documentation output directory with Markdown files for the whole command tree, including hidden commands. It does not remove stale docs before generation, so repeated runs can leave obsolete files if commands are renamed.

Dependencies/integration: integrates with the global Cobra root command and every registered command/flag in package `cmd`. It depends on filesystem permissions for the output path.

Risks/test signals: because it walks the whole mutable command tree, invalid command metadata or output permissions can fail generation. Tests cover successful generation, directory creation/access failures, generation failure under `/var`, and rejection of a file as output location.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc.go -->
