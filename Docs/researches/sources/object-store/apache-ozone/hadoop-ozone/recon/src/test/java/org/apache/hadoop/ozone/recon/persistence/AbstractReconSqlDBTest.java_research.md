# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/AbstractReconSqlDBTest.java

Purpose: This base test class creates a fully initialized Recon SQL database for tests and exposes helper APIs for DAOs, schema definitions, jOOQ configuration, DSL context, connections, and Guice injector access. It standardizes Derby-backed schema setup for Recon persistence tests.

Important APIs/types/functions: Key methods include `createReconSchemaForTest`, `init`, `getReconSqlDBModules`, `createSchema`, `getInjector`, `getConnection`, `getDataSource`, `getDslContext`, `getConfiguration`, `getDao`, `getSchemaDefinition`, and nested `DerbyDataSourceConfigurationProvider`. It uses Guice modules `JooqPersistenceModule`, `ReconSchemaGenerationModule`, `ReconDaoBindingModule`, `ReconSchemaManager`, jOOQ `DSLContext`, and `DataSourceConfiguration`.

Control flow: Before each test, `createReconSchemaForTest` receives a JUnit temp directory, initializes a Derby datasource provider under `Config/derby_recon.db`, creates a Guice injector from Recon SQL modules, constructs a DSL context from the injected `DataSource`, and calls `ReconSchemaManager.createReconSchema`. Test subclasses then retrieve DAOs/schema definitions from the injector.

State and persistence behavior: Persistent state is an embedded Derby database under the per-test temp directory. The provider configures auto-commit, two max active connections, connection timeout, max age/idle age, and `SELECT 1` validation. `init` deletes and recreates the `Config` directory to isolate tests.

Dependencies and integration points: This class is the backbone for Recon SQL persistence tests, including schema-definition tests and `TestReconReplicationManager`. It integrates Spring file cleanup, Guice injection, jOOQ, generated DAOs, schema generation, and Derby datasource configuration.

Risks: `init` calls `fail()` without including the caught exception, which can obscure setup diagnostics. Connections returned by `getConnection` are not automatically closed by this base class. Derby and SQLite dialect differences require separate tests, but most subclasses inherit Derby only. The temp `Config` directory is deleted recursively, so callers must pass isolated temp paths.

Test signals: Subclasses rely on non-null injector/configuration/DSL/connection, successful schema creation, generated DAO availability, and working CRUD against the initialized schema.
