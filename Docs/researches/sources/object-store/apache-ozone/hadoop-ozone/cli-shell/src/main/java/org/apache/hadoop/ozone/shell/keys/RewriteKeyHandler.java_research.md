# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/keys/RewriteKeyHandler.java

## Purpose
Picocli/Ozone shell component that rewrites a key generation. This research is based on a complete read of the 70-line source file.

## Important APIs and Types
Types: `RewriteKeyHandler`. Important methods: `execute`. Mixins: `replication`. Ozone/client calls observed: `getVolume`, `getBucket`, `rewriteKey`, `readKey`, `getKey`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `rewriteKey`, `readKey`, `getKey`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.keys` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Main risk is drift between CLI parsing, OzoneAddress validation, and ObjectStore client API signatures.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset.
