# sources/sync-backup/kopia/repo/maintenance/maintenance_safety_test.go

Purpose: integration tests maintenance safety around content deletion, object readability, and garbage collection.

Important APIs/types/functions: `TestMaintenanceSafety`, `verifyContentDeletedState`, `verifyObjectReadable`, and `verifyObjectNotFound`.

Control flow: the test writes repository objects, triggers maintenance and snapshot-GC style transitions, then checks whether content deleted flags and object reads match safety expectations.

State/persistence behavior: uses a real repository test environment with persisted content, manifests, and indexes.

Dependencies/integration: integrates object access, repository content state, maintenance safety presets, and test repository helpers.

Risks/test signals: detects unsafe early deletion or failure to delete after safety windows. Its exact coverage depends on test setup timing and format-specific suite execution.
