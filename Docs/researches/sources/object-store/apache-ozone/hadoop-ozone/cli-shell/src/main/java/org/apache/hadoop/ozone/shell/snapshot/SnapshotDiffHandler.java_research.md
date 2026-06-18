# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/SnapshotDiffHandler.java

## Purpose
Picocli/Ozone shell component that submits, cancels, or fetches snapshot diffs. This research is based on a complete read of the 223-line source file.

## Important APIs and Types
Types: `SnapshotDiffHandler`. Important methods: `getAddress`, `execute`, `submitSnapshotDiff`, `getSnapshotDiff`, `cancelSnapshotDiff`, `getJsonObject`, `getJsonObject`, `getJsonObject`, `getPathString`. CLI options/fields: `token` (-t/--token), `pageSize` (-p/--page-size/1000), `forceFullDiff` (--ffd/--force-full-diff), `cancel` (-c/--cancel/false), `getReport` (-r/--get-report/false), `diffDisableNativeLibs` (--dnld/--disable-native-libs-diff), `json` (--json/false). CLI parameters: `fromSnapshot`, `toSnapshot`. Mixins: `snapshotPath`. Ozone/client calls observed: `snapshotDiff`, `submitSnapshotDiff`, `cancelSnapshotDiff`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `snapshotDiff`, `submitSnapshotDiff`, `cancelSnapshotDiff`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on snapshot metadata/diff jobs; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Snapshot diff has compatibility fallback and pagination/token behavior; regressions can duplicate, omit, or misformat diff entries. Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.
