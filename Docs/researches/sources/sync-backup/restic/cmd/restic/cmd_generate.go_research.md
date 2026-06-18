# sources/sync-backup/restic/cmd/restic/cmd_generate.go

Purpose: implements `restic generate`, which writes generated man pages and shell completions for bash, fish, zsh, and PowerShell.

Important APIs/types/functions: `newGenerateCommand` registers the cobra command; `generateOptions` stores output paths; `writeManpages` uses `cobra/doc.GenManTree` with a fixed Jan 2017 date for deterministic man pages; `writeCompletion` writes either to a named file or terminal stdout when the target is `-`; `checkStdoutForSingleShell` rejects multiple stdout completion targets; `runGenerate` orchestrates all generation.

Control flow and state: the command rejects positional arguments, constructs a fresh root command with default global options, emits requested artifacts, and fails if no output option was set. Persistent writes are filesystem writes for generated files/directories only; repository state is not opened or modified.

Dependencies and integration points: depends on cobra, pflag, cobra/doc, restic `global.Options`, terminal/progress printers, and `newRootCommand`. Its output is sensitive to root command registration and command help text.

Risks: completion-to-stdout must stay single-shell to avoid interleaved output. Any command tree changes affect generated docs. File creation uses `os.Create`, so existing completion files are truncated.

Test signals: `cmd_generate_integration_test.go` verifies stdout completion headers for all shells and the multiple-stdout error path.
