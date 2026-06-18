## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/JooqPersistenceModule.java

Purpose: Guice module that wires Recon SQL persistence, jOOQ configuration, datasource transactions, and `@Transactional` interception.

Important APIs/types/functions: `configure`; provider method `getConfiguration`; provider method `provideDataSourceTransactionManager`; nested `SpringConnectionProvider`.

Control flow: binds `DataSource` to `DefaultDataSourceProvider` singleton; installs `TransactionalMethodInterceptor` for methods/classes annotated with Spring `@Transactional`; disables jOOQ logo; builds `DefaultConfiguration` with datasource, Spring-aware connection provider, and configured SQL dialect; exposes `DataSourceTransactionManager`.

State and persistence: creates the core persistence wiring used by jOOQ DAOs/schema managers. Integration with Spring transaction utilities ensures jOOQ uses transaction-bound connections.

Risks: `SQLDialect.valueOf` fails on invalid config. Provider method calls `provider.get()` directly and can create datasource before Guice singleton caching expectations if misused. Tests should cover module injection, transactional interception, dialect selection, and transaction-bound acquire/release.
