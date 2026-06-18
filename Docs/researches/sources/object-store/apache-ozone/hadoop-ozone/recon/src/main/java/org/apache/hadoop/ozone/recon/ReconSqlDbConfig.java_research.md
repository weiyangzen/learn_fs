# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSqlDbConfig.java

## Purpose
`ReconSqlDbConfig` is the annotated configuration bean for Recon's SQL database connection and jOOQ dialect.

## Important APIs, Types, And Functions
It is annotated `@ConfigGroup(prefix = "ozone.recon.sql.db")`. Configured fields include driver class, JDBC URL, username, password, autocommit, connection timeout, max active connections, max/idle ages, idle test period/query, and SQL dialect. The class provides standard getters and setters.

## Control Flow
`OzoneConfiguration.getObject(ReconSqlDbConfig.class)` populates the bean. `ReconControllerModule.getDataSourceConfiguration` reads it and adapts it to Recon's `DataSourceConfiguration` interface.

## State And Persistence
The object stores configuration values in memory. It influences persistent SQL DB location and connection-pool behavior but does not write itself.

## Dependencies And Integration Points
It depends on HDDS config annotations and is consumed by the jOOQ persistence module, codegen/runtime DAO stack, and Derby default URL resolution.

## Risks
The `@ConfigGroup` prefix and full `@Config` keys both include the same prefix style; changes must stay aligned with the config framework. Defaults are Derby-specific, so alternate dialects must set driver, URL, and dialect consistently.

## Test Signals
Tests should verify default object values, XML/config override parsing, datasource adaptation, time-unit conversion, and compatibility with Derby and SQLite settings.
