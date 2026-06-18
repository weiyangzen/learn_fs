# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUnhealthyContainersDerbyPerformance.java

## Purpose
Performance and regression benchmark for Recon's Derby-backed `UNHEALTHY_CONTAINERS` persistence path at one-million-row scale. The test documents expected behavior for the `ContainerHealthSchemaManager` APIs used by Recon container health scans and UI pagination, with Derby-specific safeguards for large `IN` clauses, delete chunking, cursor reads, and atomic replace operations.

## Important APIs, types, and functions
- Builds an in-memory Derby Recon SQL schema through Guice modules: `JooqPersistenceModule`, `ReconSchemaGenerationModule`, `ReconDaoBindingModule`, and `ReconSchemaManager`.
- Uses `ContainerHealthSchemaManager`, `UnhealthyContainersDao`, `ContainerSchemaDefinition`, jOOQ `DSLContext`, and generated table `UNHEALTHY_CONTAINERS`.
- Exercises `insertUnhealthyContainerRecords`, `getUnhealthyContainersSummary`, `getUnhealthyContainers`, `replaceUnhealthyContainerRecordsAtomically`, `getExistingInStateSinceByContainerIds`, and `batchDeleteSCMStatesForContainers`.
- Generates `UnhealthyContainerRecord` rows for five `UnHealthyContainerStates`: under-replicated, missing, over-replicated, mis-replicated, and empty-missing.

## Control flow
`@BeforeAll` creates a unique in-memory Derby database, overrides only the JDBC URL from the normal Derby configuration provider, creates schema, and captures DAO/schema manager instances. Ordered tests then insert 200,000 container IDs across five states, verify total counts, run per-state counts, group summaries, paginated reads for one state, paginated reads for all states, atomic delete-plus-insert replacement, large existing timestamp lookups, full dataset delete, and post-delete state counts. `@AfterAll` drops the in-memory database.

## State and persistence behavior
The table uses `(container_id, container_state)` uniqueness and an index shaped for state-count and state-ordered pagination. The suite intentionally shares one dataset across ordered methods: read-only checks depend on the insert, atomic replace rewrites all rows with a new timestamp while preserving row count, and the final delete removes the whole dataset. Chunk sizes are part of the persistence contract: inserts commit in 2,000-container chunks, reads page at 5,000 rows, and deletes rely on internal 1,000-ID partitioning to avoid Derby bytecode limits.

## Dependencies and integration points
The test integrates Recon SQL schema generation, jOOQ generated DAOs/tables, Derby connection configuration, `ContainerHealthTask` preservation lookups, and Recon UI-style container health pagination and summary queries. It is a local embedded database benchmark rather than a cluster test.

## Risks and edge cases
Timing thresholds are deliberately generous but still environment-sensitive. The test is order-dependent and mutates shared state, so parallelization or method reordering would invalidate it. Derby-specific statement-size limits are central: removing internal chunking can produce statement-too-complex or generated-bytecode failures for large ID lists.

## Test signals
Signals include exact row counts, per-state distribution of 200,000 rows, ordered cursor reads, one-million-row full read coverage, replacement timestamp visibility, existing `in_state_since` lookup cardinality, delete completion, and elapsed-time checks for insert, count, summary, pagination, atomic replace, and delete phases.
