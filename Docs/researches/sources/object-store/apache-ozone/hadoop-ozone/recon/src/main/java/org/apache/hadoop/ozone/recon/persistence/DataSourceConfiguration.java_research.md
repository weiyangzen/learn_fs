## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/DataSourceConfiguration.java

Purpose: abstraction for database connection and jOOQ dialect settings used by Recon persistence wiring.

Important APIs/types/functions: getters for driver class, JDBC URL, username/password, autocommit flag, connection timeout, SQL dialect, pool size, max connection/idle age, connection test statement, and idle test period.

Control flow and state: interface only; implementations supply config values to datasource providers and `JooqPersistenceModule`.

State and persistence: configuration-level integration with BoneCP, Derby/SQLite providers, and jOOQ. No direct persistence operations.

Risks: password exposed as `String`; SQL dialect is stringly typed and later converted with `SQLDialect.valueOf`. Tests should validate implementations provide compatible dialect/URL/driver and sensible pooling values for embedded vs external DBs.
