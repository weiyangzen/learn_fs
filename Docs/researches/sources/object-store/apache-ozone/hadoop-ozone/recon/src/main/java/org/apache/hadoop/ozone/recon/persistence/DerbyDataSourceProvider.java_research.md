## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DerbyDataSourceProvider.java

Purpose: provider for embedded Derby `DataSource` used by Recon persistence.

Important APIs/types/functions: constructor takes `DataSourceConfiguration`; `get()` creates the Derby database/schema then returns `EmbeddedDataSource`.

Control flow: obtains JDBC URL, calls `createNewDerbyDatabase(jdbcUrl, RECON_SCHEMA_NAME)`, logs creation errors, strips `jdbc:derby:` prefix to set database name, and sets user to Recon schema name.

State and persistence: may create Derby database/schema as a side effect. Integrates with generated jOOQ schema name and SQL DB utility.

Risks: creation exceptions are logged but do not stop datasource creation, so later failures may be delayed. It ignores password/autocommit/pool settings. Tests should cover URL conversion, schema creation invocation/failure, datasource user, and invalid path behavior.
