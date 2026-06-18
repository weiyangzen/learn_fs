# sources/sync-backup/kopia/snapshot/snapshotmaintenance/helper_test.go

Purpose: test helper for creating saved snapshots through the same policy and upload path used by maintenance tests.

Important APIs/types/functions: `createSnapshot`.

Control flow: cleans the source path, obtains the policy tree for the source, finds previous manifests, uploads the filesystem entry, sets the description, and saves the manifest.

State and persistence: writes snapshot objects and a snapshot manifest into the provided repository writer. It uses previous manifests to preserve uploader behavior around incremental/cache decisions.

Dependencies and integration points: shared by snapshot maintenance tests for realistic repository state setup. Depends on `policy.TreeForSource`, `snapshot.FindPreviousManifests`, `upload.NewUploader`, and `snapshot.SaveSnapshot`.

Risks and test signals: helper errors wrap policy and save failures, which makes maintenance test failures easier to locate. Since it normalizes source paths with `filepath.Clean`, tests should not rely on unclean path strings.
