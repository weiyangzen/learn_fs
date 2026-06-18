## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/SqliteDataSourceProvider.java

Purpose: provider for native SQLite `DataSource`, avoiding connection pooling for the embedded default database case.

Important APIs/types/functions: constructor takes `DataSourceConfiguration`; `get()` creates `SQLiteDataSource` and sets configured JDBC URL.

Control flow: no branching; direct datasource creation.

State and persistence: creates datasource only; no queries. Integrates with `DefaultDataSourceProvider` URL routing.

Risks: ignores username/password/pool/autocommit settings, consistent with embedded SQLite but important if URL points to nonstandard setup. Tests should verify URL propagation and compatibility with default Recon SQLite configuration.
