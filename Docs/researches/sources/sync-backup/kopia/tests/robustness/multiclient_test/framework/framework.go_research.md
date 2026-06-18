<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go -->
# sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go

This file defines interfaces that decouple the multiclient framework from concrete Kopia and FIO implementations. `ClientSnapshotter` embeds `robustness.Snapshotter` and adds server-client lifecycle operations such as `ConnectClient`, `DisconnectClient`, and `ServerFingerprint`. `Server` adds repository/server control functions, and `FileWriter` embeds `robustness.FileWriter` with cleanup.

There is no executable control flow; the file establishes contracts consumed by `snapshotter.go`, `filewriter.go`, and `harness.go`. The interfaces allow `snapmeta.KopiaSnapshotter` to serve both server and client roles while allowing the harness to supply factories.

Risks are interface breadth and argument ordering: wrappers rely on exact semantics for server address, fingerprint, and user IDs. Test signals are multiclient integration tests that exercise server startup, client authorization, snapshot actions, GC, and cleanup through these interfaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/multiclient_test/framework/framework.go -->
