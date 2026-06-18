# sources/sync-backup/restic/cmd/restic/flags_test.go

Purpose: smoke test ensuring command flags do not panic or conflict during help parsing.

Important APIs/types/functions: `TestFlags`.

Control flow and state: iterates immediate root command children, discards flag output, calls `ParseFlags(["--help"])`, treats `pflag: help requested` as success, and fails on other errors.

Dependencies and integration points: depends on `newRootCommand` and global options. It indirectly exercises command construction and shorthand registration.

Risks: only immediate commands are parsed, so nested subcommand conflicts may need separate coverage if not exposed through root children.

Test signals: catches duplicate shorthand definitions and command setup panics.
