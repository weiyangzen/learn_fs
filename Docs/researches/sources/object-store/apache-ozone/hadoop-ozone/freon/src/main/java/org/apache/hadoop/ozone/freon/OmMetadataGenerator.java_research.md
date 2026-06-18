## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmMetadataGenerator.java

Purpose: Freon subcommand `ommg`/`om-metadata-generator` for broad OM metadata operation benchmarking: create/read/list keys and files, bucket/volume info, and mixed workloads.

Important APIs/types/functions: options configure volume, bucket, data size, buffer, list batch size, random access, operation enum, mixed operation lists/counts, client count, OM service ID, follower-read affinity, and replication. Key methods include `call`, `initMixedOperation`, `getUsage`, `createKeyArgsBuilder`, `realTimeStatusSupplier`, `applyOperation`, `performWriteOperation`, `performReadOperation`, `getOMFollowerNodeIds`, and `changeInitialProxyForFollowerRead`.

Control flow: if `--ophelp` or missing operation, prints usage. MIXED maps thread sequence IDs to operation enum values based on `--ops`/`--opsnum`. It initializes Freon, creates content generator and per-thread key args builder, ensures target bucket, creates multiple Ozone clients, optionally points clients at OM followers, then runs `applyOperation`. The operation switch performs create/read/lookup/list/info actions via `ClientProtocol` or `OzoneManagerProtocol`, timing each operation name separately.

State and persistence behavior: creates keys/files when using create operations; read/list/info operations are read-only. Local state includes client array, thread-local args builders, operation mapping, timers, and replication config.

Dependencies and integration points: Ozone client protocol, OM protocol, HA follower-read failover transport, Dropwizard metrics, content generation, replication mixin.

Risks: read/list operations require pre-existing sufficient objects; `randomOp` can create/read the same key concurrently; follower affinity only supports `Hadoop3OmTransport`; mixed operation mutates the instance `operation` field from worker threads, which is a concurrency hazard.

Test signals: operation-specific timers, rate display, validation that list operations throw when there are not enough objects, and integration coverage for follower-read affinity.
