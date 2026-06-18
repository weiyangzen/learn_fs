## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/StaleRecoveringContainerScrubbingService.java

Purpose: Provides a datanode background service that marks stale recovering containers unhealthy after their recovery timeout expires.

Important APIs and functions: The constructor configures the `BackgroundService` name, interval, thread pool, timeout, and `ContainerSet`. `getTasks()` scans the recovering-container iterator, enqueues `RecoveringContainerScrubbingTask` for expired entries, and removes them from the tracking iterator. The task `call()` fetches the container and calls `markContainerUnhealthy()`.

Control flow and state: The service assumes the `ContainerSet` recovering-container iterator is ordered by timeout, because it stops at the first non-expired entry. Tasks carry only container ID and `ContainerSet` reference. Missing containers are silently ignored by the task.

Persistence and dependencies: Marking unhealthy delegates to the container implementation, which persists container state through its metadata file. The service depends on HDDS background task queues and `ContainerSet.RecoveringContainer`.

Risks: Iterator ordering is essential; if entries are unordered, later expired containers can be skipped. Removing entries before task execution means a task failure may lose the pending scrub marker. The task marks any currently loaded container unhealthy without rechecking state or timeout.

Test signals: Cover ordered timeout scanning, first non-expired break behavior, iterator removal, missing containers, marking loaded recovering containers unhealthy, repeated service intervals, and task exceptions under background service timeout.
