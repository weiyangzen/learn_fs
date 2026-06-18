## sources/test-tools/syzkaller/pkg/lore-relay/commands_test.go

Purpose: unit tests for Lore command extraction.

Important APIs/types/functions: `TestMapCommands`.

Control flow: constructs parsed email fixtures with upstream/reject/unreject/comment cases and compares generated dashboard requests.

State and persistence: none.

Dependencies and integration: validates the contract between email parser output and dashboard API request fields.

Risks: does not cover relay-level DKIM/multiple-command decisions.

Test signals: direct mapping regression coverage.
