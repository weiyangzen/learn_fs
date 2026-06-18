# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/DeleteSnapshotHandler.java

## Purpose
Picocli/Ozone shell component that deletes a bucket snapshot. This research is based on a complete read of the 61-line source file.

## Important APIs and Types
Types: `DeleteSnapshotHandler`. Important methods: `getAddress`, `execute`. CLI parameters: `snapshotName`. Mixins: `snapshotPath`. Ozone/client calls observed: `deleteSnapshot`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `deleteSnapshot`. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.
