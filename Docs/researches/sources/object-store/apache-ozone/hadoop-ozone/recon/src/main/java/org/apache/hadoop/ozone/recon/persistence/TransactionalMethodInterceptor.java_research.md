## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/TransactionalMethodInterceptor.java

Purpose: AOP Alliance method interceptor that implements Spring-managed transactions for Guice-bound Recon persistence methods.

Important APIs/types/functions: constructor receives provider for `DataSourceTransactionManager`; `invoke(MethodInvocation)`.

Control flow: obtains a transaction with default definition, proceeds with invocation, commits only if this call opened a new transaction, ignores `UnexpectedRollbackException` during commit, rolls back new transactions on `Exception`, and rethrows.

State and persistence: no direct persistence; controls transaction boundaries for datasource/jOOQ operations. Integrates with `JooqPersistenceModule` interceptors.

Risks: catches only `Exception`, not `Error`; unchecked `RuntimeException` is covered, but serious throwables may skip rollback. Ignoring `UnexpectedRollbackException` can hide transaction failures. Tests should cover nested transactions, commit/rollback, checked/runtime exceptions, unexpected rollback handling, and transaction manager provider behavior.
