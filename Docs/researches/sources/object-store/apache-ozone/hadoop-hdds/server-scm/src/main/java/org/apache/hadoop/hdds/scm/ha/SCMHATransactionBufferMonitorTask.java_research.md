# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHATransactionBufferMonitorTask.java

Purpose: Periodic task that asks the HA transaction buffer to flush when its configured interval or snapshot wait policy requires it.

Important APIs and types: Implements `Runnable`; constructed with `SCMHADBTransactionBuffer` and a flush interval. `run` delegates to `transactionBuffer.flushIfNeeded(flushInterval)`.

Control flow: The task is scheduled by `SCMHAManagerImpl` through `BackgroundSCMService`. Each run catches `IOException` and logs failure without throwing out of the background service.

State and persistence behavior: No local state beyond the buffer reference and interval. Persistence is entirely delegated to the transaction buffer, which may flush batched RocksDB mutations and transaction metadata.

Dependencies and integration points: Connects SCM HA transaction buffering to the generic SCM background-service framework.

Risks and test signals: Because failures are logged and swallowed, persistent flush failure may repeat without stopping SCM immediately. Tests should assert delegation, configured interval use, and that thrown IOExceptions are contained.
