# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdGenerator.java

Purpose: HA-safe sequence ID allocator for SCM ids such as local id, deleted transaction id, container id, and certificate id.

Important APIs and types: `getNextId`, `invalidateBatch`, `reinitialize`, static upgrade helpers, inner `StateManager`, `StateManagerImpl`, `StateManagerImpl.Builder`, and `Batch`. `StateManager.allocateBatch` is annotated `@Replicate` and proxied through `SequenceIdGeneratorStateManagerInvoker`.

Control flow: `getNextId` locks globally, serves from an in-memory batch when possible, otherwise CAS-replicates the DB last id from expected to next batch end. Failed CAS reloads the last id and retries. Leadership change invalidates unused batch ranges so a new leader allocates after the persisted last id.

State and persistence behavior: Runtime batches track `lastId` and `nextId`. `StateManagerImpl` caches DB last ids in a concurrent map and persists new last ids through `DBTransactionBuffer.addToBuffer`. Upgrade helpers seed sequence ids from existing local-id time, deleted-block transaction table, container table, and certificate tables.

Dependencies and integration points: Used by SCM managers that allocate persistent ids and reinitialized from `SCMMetadataStore` after checkpoint install.

Risks and test signals: Batch invalidation intentionally skips unused ids to preserve monotonicity. Certificate ids allocate one at a time. Tests should cover CAS retry, batch boundaries, leader invalidation, reinitialize clearing cache, upgrade id derivation, root certificate cleanup, and overflow preconditions.
