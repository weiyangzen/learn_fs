# sources/sync-backup/syncthing/lib/config/testdata/issue-1262.xml

## sources/sync-backup/syncthing/lib/config/testdata/issue-1262.xml

Purpose: Regression fixture for Windows drive-root folder path handling.

Important data: Version 7 config has folder path `e:` with read-only legacy flag.

Control flow and state: On Windows, filesystem initialization should resolve the path to `e:\` after config load.

Dependencies and integration: Used by `TestIssue1262`, skipped on non-Windows platforms.

Risks and test signals: Protects platform-specific path semantics during migration/preparation.
