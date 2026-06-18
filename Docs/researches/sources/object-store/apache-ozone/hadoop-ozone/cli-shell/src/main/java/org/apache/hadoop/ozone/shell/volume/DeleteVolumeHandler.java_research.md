# sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/volume/DeleteVolumeHandler.java

## Purpose
Picocli/Ozone shell component that deletes a volume, optionally recursively. This research is based on a complete read of the 237-line source file.

## Important APIs and Types
Types: `DeleteVolumeHandler`, `BucketCleaner`. Important methods: `execute`, `deleteVolumeRecursive`, `cleanOBSBucket`, `cleanFSBucket`, `run`, `doCleanBuckets`. CLI options/fields: `bRecursive` (-r), `threadNo` (-t/--threads/--thread), `yes` (-y/--yes). Ozone/client calls observed: `getVolume`, `getBucket`, `deleteKeys`, `listKeys`, `deleteVolume`.

## Control Flow
Picocli parses options and `Handler` dispatches `execute(...)` with an `OzoneClient` and parsed `OzoneAddress`/object. The command resolves volume/bucket/key or tenant/token identifiers and delegates persistence to ObjectStore/OzoneVolume/OzoneBucket calls: `getVolume`, `getBucket`, `deleteKeys`, `listKeys`, `deleteVolume`. I/O resources are scoped with try-with-resources so streams, filesystem handles, and writers close on success or exception. Iterator loops page through server-side listings and print or batch results incrementally. Recursive volume deletion fans bucket cleanup out through a fixed thread pool and shared atomic counters. Branching enforces command flags, layout-specific behavior, validation failures, and compatibility fallbacks before mutating the server.

## State and Persistence
Local handler fields hold parsed command options for one invocation. Durable effects are remote Ozone Manager/ObjectStore mutations on key namespace and key data, volume metadata/quota/ownership; this file itself does not persist local state.

## Dependencies and Integration Points
Package `org.apache.hadoop.ozone.shell.volume` integrates with sibling shell commands through picocli subcommands and shared handler/address classes. Primary dependencies: picocli command binding; Ozone client object-store API; shared shell handler/address utilities; Hadoop filesystem/path utilities; HDDS config/replication helpers. Runtime integration boundary is the Ozone client API; the command is a thin CLI adapter over server-side ObjectStore/OzoneBucket/OzoneVolume behavior.

## Risks and Edge Cases
Destructive operations need strong validation because a parsed address or flag mistake can remove server-side data or credentials. Recursive deletion combines concurrency, batch deletes, and filesystem deletion for FSO/legacy buckets; interruption and partial failure handling are important.

## Test Signals
URI/address parsing behavior is exercised by `TestOzoneAddress` and client-creation tests in this subset. Destructive and recursive flows need layout-specific integration tests for OBJECT_STORE, LEGACY, and FSO buckets.
