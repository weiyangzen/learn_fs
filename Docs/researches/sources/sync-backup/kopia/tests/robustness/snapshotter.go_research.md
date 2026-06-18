<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/snapshotter.go

This file defines the `robustness.Snapshotter` interface and snapshot creation stats. The interface covers repository connection, snapshot create/restore/restore-and-compare, delete, GC, list, arbitrary command execution, and cleanup as needed by the engine.

`CreateSnapshotStats` records snapshot start and end times. The engine uses these values for per-action logging/stats. Implementations include `snapmeta.KopiaSnapshotter` and `MultiClientSnapshotter`.

There is no state here, but this contract is the main integration point between engine actions and Kopia repositories. Risks are broad interface responsibilities, inconsistent implementation of no-op/errors, and optional methods like `Run`/`Cleanup` tying tests to Kopia-specific behavior. Test signals are full robustness and multiclient suites.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapshotter.go -->
