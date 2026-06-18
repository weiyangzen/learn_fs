# sources/sync-backup/restic/internal/fs/path_prefix_test.go

Purpose: Unit tests for `HasPathPrefix`.

Important APIs: `fromSlashAbs` and `TestHasPathPrefix`.

Control flow and state: Converts slash paths to OS paths, adding `c:` to absolute paths on Windows, then checks a table of base/path/result cases.

Dependencies and integration: Validates path-prefix logic used by VSS mount-point routing.

Risks: Tests intentionally preserve case sensitivity even on Windows by using the function contract rather than filesystem behavior.

Test signals: Good coverage for boundary cases that could otherwise cause VSS to route sibling paths into the wrong snapshot.
