# sources/sync-backup/kopia/snapshot/policy/os_snapshot_policy_test.go

Purpose: verifies `OSSnapshotMode` defaulting and string conversion.

Important APIs/types/functions: `TestOSSnapshotMode` uses `NewOSSnapshotMode`, nil-pointer `OrDefault`, and `OSSnapshotMode.String`.

Control flow: asserts nil mode returns provided default, explicit mode overrides default, and each constant maps to expected string.

State and persistence behavior: no persistence; protects presentation/default behavior used by policy consumers.

Dependencies/integration: uses `testify/assert`.

Risks: does not cover merge behavior or JSON representation.

Test signals: focused coverage for mode helper semantics.
