# sources/sync-backup/git-lfs/subprocess/subprocess_test.go

Purpose: unit tests for shell quoting and command formatting utilities.

Important test types/functions: `ShellQuoteTestCase`, `TestShellQuote`, `FormatForShellQuotedArgsTestCase`, `TestFormatForShellQuotedArgs`, `FormatForShellTestCase`, `TestFormatForShell`, `FormatPercentSequencesTestCase`, and `TestFormatPercentSequences`.

Control flow: table-driven tests assert exact quoting for spaces, backslashes, quotes, mixed quotes, shell-wrapped command strings, and percent replacement with shell quoting.

State/persistence behavior: no persistence.

Dependencies/integration: protects `ssh.FormatArgs`, merge-tool command formatting, and any shell invocation built from these helpers.

Risks: tests do not execute a shell; they validate string construction only. `FormatForShell` is deliberately unquoted and tested as such.

Test signals: failures indicate changed quoting contracts that can affect custom SSH commands or file-name handling.
