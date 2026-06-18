# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/ReplicatedSizeOfFilesUpgradeAction.java

Purpose: `ReplicatedSizeOfFilesUpgradeAction` triggers a full NSSummary rebuild when the namespace summary model gains replicated file size totals.

Important APIs and types: annotated for `REPLICATED_SIZE_OF_FILES`. `execute(DataSource)` retrieves the global Guice injector, obtains `ReconTaskController`, queues a manual reinitialization event, and throws if queueing is not successful.

Control flow and integration: layout finalization runs this action after the corresponding feature version becomes pending. Reinitialization is performed asynchronously by the controller but this action treats failure to queue as fatal.

State and persistence: no direct SQL mutation. The durable effect is indirect: Recon tasks rebuild namespace summary state after the queued event is processed.

Dependencies: global Guice injector, `ReconTaskController`, `ReconTaskReInitializationEvent`, SLF4J.

Risks and test signals: success only confirms queueing, not rebuild completion. Missing injector or retry-later result fails the upgrade. Tests should cover missing injector, queue success, queue retry/failure, and thrown runtime wrapper.
