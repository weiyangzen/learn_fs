<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go

This file provides `MultiClientSnapshotter`, a `robustness.Snapshotter` implementation that starts one server repository and lazily creates per-client snapshotters. It stores a server adapter, client map, base dir, and client factory.

`ConnectOrCreateRepo` connects/creates the server repository and sets a global keep-latest policy plus compression. Snapshot, restore, compare, delete, and list operations call `createOrGetSnapshotter` to delegate by client context. `RunGC` intentionally runs on the server. `Cleanup` and `CleanupClient` disconnect clients, remove users from the server, clean client resources, and clean server resources. `createOrGetSnapshotter` authorizes the client, connects it with the server fingerprint, and registers it.

State includes long-lived server command, server fingerprint, per-client config dirs, and authorized users. Dependencies are `snapmeta.KopiaSnapshotter`, context client identities, and Kopia server ACL/user behavior. Risks include duplicate lazy creation under concurrent first use, leaked client temp dirs if authorization/connect fails after creation, and server user removal errors only being logged. Integration is central to multiclient tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/snapshotter.go -->
