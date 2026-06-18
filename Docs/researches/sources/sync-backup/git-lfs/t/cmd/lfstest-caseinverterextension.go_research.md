# sources/sync-backup/git-lfs/t/cmd/lfstest-caseinverterextension.go

Purpose: test Git LFS pointer extension that swaps character case during clean/smudge.

Important functions/state: `gitDir`, `main`, `openLog`, and `logErrorAndExit`.

Control flow: validates args are `clean -- <path>` or `smudge -- <path>`, requires `.git` to exist and be a directory, optionally logs operation/path to `LFSTEST_EXT_LOG`, reads stdin rune by rune, swaps upper/lowercase Unicode runes, writes stdout, and exits.

State/persistence behavior: reads `.git` metadata, appends to optional log file, otherwise streams data only.

Dependencies/integration: used by integration tests for extension filters and clean/smudge behavior.

Risks: validates `.git` in current working directory only, so tests must run from repo root. Unicode case conversion may expand some runes but writes strings directly.

Test signals: transformed content and optional log entries.
