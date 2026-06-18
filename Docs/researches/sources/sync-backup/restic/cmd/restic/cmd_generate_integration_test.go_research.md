# sources/sync-backup/restic/cmd/restic/cmd_generate_integration_test.go

Purpose: integration coverage for `runGenerate` when completions are written to stdout.

Important APIs/types/functions: `testRunGenerate` wraps `runGenerate` with `withCaptureStdout`; `TestGenerateStdout` drives bash, fish, zsh, and powershell options plus a negative case with two `-` outputs.

Control flow and state: tests use an in-memory stdout buffer and do not create repositories or files. Each shell case asserts the generated text contains a shell-specific completion header.

Dependencies and integration points: depends on integration terminal helpers, `global.Options`, and `internal/test` assertions. It indirectly verifies cobra completion generation through the full root command tree.

Risks: header-string assertions are lightweight and can fail if cobra changes comment wording while completions remain valid. The test does not verify generated files or man pages.

Test signals: confirms each stdout mode works and `checkStdoutForSingleShell` blocks ambiguous multi-shell stdout output.
