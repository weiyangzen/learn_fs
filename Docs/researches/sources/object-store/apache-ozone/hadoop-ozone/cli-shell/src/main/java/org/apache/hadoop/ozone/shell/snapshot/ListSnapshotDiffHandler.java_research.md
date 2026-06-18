# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/snapshot/ListSnapshotDiffHandler.java

## Purpose
Picocli/Ozone shell component that lists snapshot diff jobs. This research is based on a complete read of the 75-line source file.

## Important APIs and Types
Types: `ListSnapshotDiffHandler`. Important methods: `getAddress`, `execute`. CLI options/fields: `jobStatus` (--job-status/in_progress), `listAllStatus` (--all-status/false). Mixins: `snapshotPath`, `listOptions`. Ozone/client calls observed: `listSnapshotDiffJobs`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `listSnapshotDiffJobs`. Iterator loops page through server-side listings and print or batch results incrementally. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local state is limited to parsed CLI options, temporary collections, and output formatting. Remote calls are read-oriented unless sibling APIs invoked by the command perform mutation.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.snapshot` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Snapshot diff has compatibility fallback and pagination/token behavior; regressions can duplicate, omit, or misformat diff entries.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Snapshot commands should be validated with mocked ObjectStore tests plus integration coverage for OM feature compatibility.
