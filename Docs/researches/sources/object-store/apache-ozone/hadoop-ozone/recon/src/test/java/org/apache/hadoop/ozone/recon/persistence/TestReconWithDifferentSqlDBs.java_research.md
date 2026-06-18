# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconWithDifferentSqlDBs.java

Purpose: This parameterized suite verifies that Recon schema setup and generated DAO bindings work with both Derby and SQLite datasource configurations. It is a cross-dialect smoke test for schema generation, Guice bindings, jOOQ configuration, DAO CRUD, and DSL operations.

Important APIs/types/functions: The test uses `AbstractReconSqlDBTest`, `DerbyDataSourceConfigurationProvider`, nested `SqliteDataSourceConfigurationProvider`, `DataSourceConfiguration`, `RECON_DAO_LIST`, `ReconTaskStatusDao`, `ReconTaskStatus`, jOOQ generated table `RECON_TASK_STATUS`, `SQLDialect.SQLITE`, Derby/SQLite driver constants, and JUnit `@TempDir` plus `@MethodSource`.

Control flow: `parametersSource` creates one Derby temp directory and one SQLite temp directory. `testSchemaSetup` constructs an `AbstractReconSqlDBTest` with the provider, manually invokes `createReconSchemaForTest`, asserts core objects and every DAO binding are non-null, inserts one task status record through the DAO, deletes rows through jOOQ DSL, and verifies the DAO sees zero records afterward.

State and persistence behavior: Persistent state is either embedded Derby at `derby_recon.db` or SQLite at `recon_sqlite.db` under temp directories. Both providers use auto-commit, two active connections, timeout/age settings, and `SELECT 1` validation.

Dependencies and integration points: This test guards Recon's SQL abstraction across supported local databases. It integrates datasource providers, schema generation, Guice DAO binding list, generated DAOs, and direct jOOQ DSL operations.

Risks: `@TempDir` is static, which can be sensitive to JUnit configuration. The test covers one DAO/table deeply and only non-null construction for the rest. It does not compare metadata column types across dialects. SQLite and Derby temp DBs share the same parent temp path but use distinct child directories.

Test signals: Injector, jOOQ configuration, DSL context, connection, and every DAO in `RECON_DAO_LIST` are non-null for both providers; inserting `ReconTaskStatus("TestTask", 1L, 2L, 1, 0)` yields one row; deleting through `RECON_TASK_STATUS` removes one row; DAO `findAll` returns zero after delete.
