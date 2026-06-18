## sources/sync-backup/syncthing/lib/model/testos_test.go

Purpose: small test helper module defining common fatal/panic convenience functions for model tests.

Important APIs: `fatal` is the shared interface between `*testing.T` and `*testing.B` requiring `Fatal` and `Helper`. `must` marks itself as helper and fatals on non-nil error. `mustV` returns a value or panics on error for use where a testing object is not available.

Control flow and state: stateless helpers only.

Dependencies and integration points: used throughout model tests to reduce repetitive error handling. `mustV` is suitable for package-level or inline initialization where failing a test directly is not available.

Risks: `mustV` panics instead of failing a specific test, so use in concurrent or shared setup can produce less localized failures.

Test signals: no tests for the helpers; behavior is trivial and exercised indirectly by many model tests.
