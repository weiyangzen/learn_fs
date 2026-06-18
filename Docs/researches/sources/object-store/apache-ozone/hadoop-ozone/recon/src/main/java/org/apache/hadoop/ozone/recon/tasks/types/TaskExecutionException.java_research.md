# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/types/TaskExecutionException.java

Purpose: `TaskExecutionException` is a runtime wrapper that associates an exception thrown during async task execution with a Recon task name.

Important APIs and types: constructor accepts `taskName` and cause, passes the cause to `RuntimeException`, and stores the task name. `getTaskName()` returns it.

Control flow and integration: `ReconTaskControllerImpl` throws this wrapper inside `CompletableFuture` suppliers when task calls fail. Exception handlers inspect the cause, extract task name, increment metrics, log context, and update task status.

State and persistence: no durable state; it carries in-memory exception metadata.

Dependencies: Java runtime exceptions.

Risks and test signals: the wrapper uses `super(cause)` rather than a message, so logs rely on cause and separate task-name logging. Tests should cover task-name extraction and cause preservation.
