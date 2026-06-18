<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go

This file implements `robustness.Snapshotter` using Kopia CLI commands plus `fswalker` comparison. `KopiaSnapshotter` embeds `kopiaConnector` and owns a `WalkCompare` for data fingerprints.

`ConnectOrCreateRepo` connects/creates a repo and sets a permissive retention policy plus compression. Snapshot creation first gathers an fswalker fingerprint, runs `kopia snapshot create`, records timing stats, and returns snapshot ID plus fingerprint. Restore methods run `snapshot restore` and either gather a new fingerprint or compare against saved fingerprint data. Delete, GC, list, arbitrary `Run`, client authorization, server fingerprint, and cleanup delegate to the Kopia runner/connector. Upgrade helpers read repository status JSON and run repository format upgrade with env gating.

State includes Kopia config, server process/fingerprint, and no long-lived fswalker data beyond returned blobs. Dependencies are CLI JSON shape, `clock`, `fswalker`, and robustness stats types. Risks include CLI output parsing, restore target overwrite behavior, upgrade side effects, and filters hiding real metadata drift. Tests cover connector/snapshotter upgrade paths and end-to-end robustness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_snapshotter.go -->
