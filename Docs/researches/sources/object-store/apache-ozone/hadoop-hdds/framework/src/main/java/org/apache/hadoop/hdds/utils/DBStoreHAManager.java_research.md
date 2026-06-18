# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/DBStoreHAManager.java

Purpose: `DBStoreHAManager` is an extension interface for DB stores that can expose HA transaction metadata for SCM and OM.

Important APIs/types/functions: default `getTransactionInfoTable()` returns `null`; implementations can override to return a `Table<String, TransactionInfo>`.

Control flow: callers can check whether a DB store/manager supplies a transaction info table and use it for HA state, snapshot, or transaction tracking.

State and persistence: interface only. The returned table, when implemented, is persistent DB-backed state.

Dependencies/integration: depends on local DB `Table` abstraction and `TransactionInfo`. Used by HA-aware DB implementations.

Risks: default null return requires callers to handle absence explicitly. A default no-op can hide missing implementation if callers assume HA metadata exists.

Test signals: HA DB and checkpoint tests provide indirect coverage through concrete managers; no direct unit test for this interface was found.
