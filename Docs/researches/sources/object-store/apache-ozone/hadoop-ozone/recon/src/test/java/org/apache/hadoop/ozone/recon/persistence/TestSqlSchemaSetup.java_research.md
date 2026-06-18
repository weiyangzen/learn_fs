# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSqlSchemaSetup.java

Purpose: This parameterized smoke test validates basic Recon SQL schema setup using the default Derby base class and confirms task status rows can be inserted with multiple `lastTaskRunStatus` values.

Important APIs/types/functions: It extends `AbstractReconSqlDBTest` and uses `RECON_DAO_LIST`, `ReconTaskStatusDao`, `ReconTaskStatus`, JUnit `@ParameterizedTest`, and `@ValueSource(ints = {0, 1, -1})`.

Control flow: For each status value, the inherited `@BeforeEach` creates the Recon schema. The test asserts injector, jOOQ configuration, DSL context, and connection are non-null, verifies every DAO binding in `RECON_DAO_LIST`, inserts one `ReconTaskStatus` with the parameterized status, and asserts one row exists.

State and persistence behavior: Persistent state is the per-test Derby DB from `AbstractReconSqlDBTest`. Each parameter invocation gets its own setup and inserts one task status row with status 0, 1, or -1.

Dependencies and integration points: This is a broad wiring smoke test for Recon SQL schema generation and DAO binding. It specifically guards task status support for success, failure, and sentinel/unknown status values.

Risks: It verifies availability of all DAOs but only exercises one DAO. It does not validate table definitions or clean up rows within an invocation, relying on isolated temp DB setup. Connection lifecycle is not explicitly closed in the test.

Test signals: Non-null injector/configuration/DSL/connection, non-null all DAO bindings, and exactly one task status row after insertion for each of `lastTaskRunStatus` 0, 1, and -1.
