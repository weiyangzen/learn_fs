# sources/sync-backup/syncthing/lib/config/testdata/issue-1750.xml

## sources/sync-backup/syncthing/lib/config/testdata/issue-1750.xml

Purpose: Regression fixture for preserving trimmed option values through migration.

Important data: Version 9 config has listen addresses and global announce servers padded with whitespace.

Control flow and state: `OptionsConfiguration.prepare` unique-trims options before migrations run, preserving the exact intended address strings.

Dependencies and integration: Used by `TestIssue1750`.

Risks and test signals: Protects migration ordering; if migrations ran before option preparation, old schemas could be incorrectly rewritten.
