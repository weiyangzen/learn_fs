# sources/sync-backup/kopia/snapshot/policy/expire.go

Purpose: applies snapshot retention policy by identifying and optionally deleting expired snapshot manifests.

Important APIs/types/functions: `ApplyRetentionPolicy`, `getExpiredSnapshots`, and `getExpiredSnapshotsForSource`.

Control flow: `ApplyRetentionPolicy` delegates to a remote repository server when the repository implements `RemoteRetentionPolicy` and the source matches the connected client user/host. Otherwise it lists snapshots, computes expired IDs, and deletes them only when `reallyDelete` is true. Expiration groups manifests by source, loads the effective policy for each source, calls `RetentionPolicy.ComputeRetentionReasons`, and deletes snapshots with no retention reasons and no pins.

State and persistence behavior: dry-run mode returns candidate manifest IDs without mutation. Real delete removes snapshot manifests via `DeleteManifest`; underlying object/content garbage collection is separate. `RetentionReasons` are transient fields on loaded manifests.

Dependencies/integration: depends on snapshot listing/grouping, repository writer/delete APIs, remote retention interface, manifest IDs, and retention policy implementation from other files.

Risks: deletion is manifest-only and assumes later maintenance handles unreachable content. Remote delegation only applies to the client's own source; other sources are processed client-side. Pins prevent deletion even when retention reasons are empty.

Test signals: retention policy behavior is likely covered in retention tests outside this subset; this file has no direct tests here.
