# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server.events` as the simple event queue implementation for HDDS/Ozone server components.

Important APIs/types/functions: it declares only the package and package-level Javadoc. The substantive APIs in the package include `EventQueue`, `EventPublisher`, `EventHandler`, `EventExecutor`, `SingleThreadExecutor`, `FixedThreadPoolWithAffinityExecutor`, and watcher/metrics support classes.

Control flow: package-level documentation has no runtime control flow.

State and persistence: none.

Dependencies/integration: the package forms the asynchronous event bus used by SCM, Recon, safe mode, node/container/pipeline handlers, and tests.

Risks: none in this file; the operational risks belong to the concrete queue/executor classes.

Test signals: package functionality is covered by framework unit tests such as `TestEventQueue`, `TestEventQueueChain`, and `TestEventWatcher`.
