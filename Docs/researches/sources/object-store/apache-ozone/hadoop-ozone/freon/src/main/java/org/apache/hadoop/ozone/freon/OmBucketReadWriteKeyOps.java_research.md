## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteKeyOps.java

Purpose: Freon subcommand `obrwk` that measures mixed key create/list behavior through Ozone bucket APIs.

Important APIs/types/functions: extends `AbstractOmBucketReadWriteOps`. Options configure volume, bucket, read/write key counts, OM service ID, and replication mixin. Implements `display`, `initialize`, `mainMethod`, `createPath`, `getReadCount`, and `create`.

Control flow: base `call` initializes shared workload config, then `initialize` resolves replication, ensures target volume/bucket, obtains `OzoneBucket`, and runs `mainMethod`. Each main task precreates/list-reads keys under `/readPath`, writes batches under `/writePath`, and prints totals.

State and persistence behavior: persists keys in the target Ozone bucket. Local state holds metadata map, replication config, and bucket handle.

Dependencies and integration points: Ozone client object store APIs, `FreonReplicationOptions`, inherited content writer and metrics.

Risks: `bucket` is used by concurrent nested threads and must be thread-safe; list path includes leading/trailing OM separators; repeated runs can accumulate random keys and affect list counts.

Test signals: listStatus result size, created key count, and `om-bucket-read-write-ops` timer values.
