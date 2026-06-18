## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DefaultDataSourceProvider.java

Purpose: Guice provider that creates the Recon SQL `DataSource` based on configured JDBC URL.

Important APIs/types/functions: injected `DataSourceConfiguration`; `get()` chooses Derby provider, SQLite provider, or a BoneCP pooled datasource.

Control flow: JDBC URLs containing `derby` delegate to `DerbyDataSourceProvider`; containing `sqlite` delegate to `SqliteDataSourceProvider`; all others configure BoneCP with driver, URL, credentials, autocommit, timeouts, pool size, age limits, idle test period, and test statement.

State and persistence: creates connection pools or embedded datasources; no queries itself. Integrates with `JooqPersistenceModule` and SQL schema classes.

Risks: substring URL detection can misclassify unusual URLs. Embedded DBs bypass pooling by design. Credentials are set directly on BoneCP. Tests should cover URL routing, BoneCP property mapping, Derby/SQLite native providers, and bad driver/URL behavior.
