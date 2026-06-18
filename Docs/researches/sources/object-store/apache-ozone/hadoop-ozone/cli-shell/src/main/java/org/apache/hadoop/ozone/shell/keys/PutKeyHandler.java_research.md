# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/PutKeyHandler.java

## Purpose
Picocli/Ozone shell component that uploads a local file as a key. This research is based on a complete read of the 172-line source file.

## Important APIs and Types
Types: `PutKeyHandler`. Important methods: `execute`, `async`, `createOrReplaceKey`, `stream`. CLI options/fields: `stream` (--stream), `expectedGeneration` (--expectedGeneration). CLI parameters: `fileName`. Mixins: `replication`. Ozone/client calls observed: `getVolume`, `getBucket`, `createKey`, `rewriteKey`, `createStreamKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `createKey`, `rewriteKey`, `createStreamKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Upload path depends on replication resolution, chunk size, expected generation, and streaming incompatibility with EC replication. Validation exceptions are part of user-visible CLI behavior and should remain stable.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.
