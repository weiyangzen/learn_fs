# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReplicationConfigPreference.java

Purpose: This abstract non-HA integration test verifies the precedence order for replication configuration when creating keys through `ozone sh`. It exhaustively combines server defaults, client configuration overrides, bucket replication config, and key CLI replication options.

Important APIs and types: It uses `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `OzoneShell`, `MiniOzoneCluster`, `OzoneClient`, `OzoneVolume`, `OzoneBucket`, `OzoneKeyDetails`, `TestDataUtil`, `TestHelper.setConfig`, and config keys `OZONE_REPLICATION`, `OZONE_REPLICATION_TYPE`, `OZONE_SERVER_DEFAULT_REPLICATION_KEY`, and `OZONE_SERVER_DEFAULT_REPLICATION_TYPE_KEY`.

Control flow: `init` creates a client and test file, saves and unsets existing replication-related configuration, creates one volume, and stores the volume handle. The parameter source builds all 81 combinations from `null`, RATIS/THREE, and EC 3-2 configs for server, client, bucket, and key levels. Each test updates OM server defaults, creates an `OzoneShell` with optional client overrides and OM address override, creates a bucket with optional replication flags, puts a key with optional replication flags, then validates the actual key config.

State and persistence behavior: The test mutates live OM replication defaults and restores saved config in `@AfterAll`. It persists buckets and keys in a shared volume, with random names per combination. Bucket metadata stores the bucket-level replication config; key metadata stores the resolved final replication config.

Dependencies and integration points: It connects shell CLI flags, client-side config overrides, OM server default replication, bucket metadata, and key creation. It is exposed through `NonHATests.ReplicationConfigPreference`, so it runs in the shared non-HA cluster context.

Risks: The comment labels both client and bucket as precedence step 2, but the implemented order is key CLI, client config, bucket config, server default, then RATIS/THREE fallback. The test creates many objects and relies on random names rather than cleanup. Direct OM config mutation must be restored to avoid contaminating later tests.

Test signals: For every combination, the bucket's stored replication config equals the bucket CLI config, and the key's config matches the expected precedence. Assertion messages include the key, bucket, client, and server replication descriptions to diagnose failures.
