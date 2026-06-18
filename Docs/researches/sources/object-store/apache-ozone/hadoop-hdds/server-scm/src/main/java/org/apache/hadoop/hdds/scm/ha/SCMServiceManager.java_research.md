# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMServiceManager.java

Purpose: Synchronized registry and broadcaster for SCM background services.

Important APIs and types: `register`, `notifyStatusChanged`, `notifyEventTriggered`, `start`, and `stop` operate over an internal `List<SCMService>`.

Control flow: Register validates non-null services and appends them. Notification methods iterate over all services and call the relevant hook. `start` invokes each service, catching `SCMServiceException` and logging warnings. `stop` calls each service's stop method.

State and persistence behavior: Maintains only in-memory service registration order. No persistence.

Dependencies and integration points: Used by `SCMHAManagerImpl` to register the transaction-buffer monitor, by `SCMStateMachine` leadership callbacks, and by other SCM server code that coordinates background services.

Risks and test signals: Coarse synchronization prevents concurrent mutation but means a slow service hook blocks all notifications. `stop` does not catch runtime failures. Tests should cover registration ordering, null rejection, notification fan-out, start exception isolation, and stop invocation.
