# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSServerWebApp.java

## Purpose
`HttpFSServerWebApp` bootstraps the HttpFS servlet application, exposes the singleton server context, initializes services and metrics, and cleans them up on shutdown.

## Important APIs, Types, and Functions
The class extends `ServerWebApp` with server name `httpfs`. Static atomics hold the singleton webapp and metrics instances. `init()` enforces singleton initialization, calls `super.init()`, loads the admin group from `httpfs.admin.group`, logs the target filesystem, and initializes metrics. `destroy()` clears the singleton, shuts down metrics, and delegates to the parent. `setMetrics()` creates `HttpFSServerMetrics`, starts `JvmPauseMonitor`, sets `FSOperations` buffer size, and initializes the default metrics system. Accessors include `get()`, `getMetrics()`, and `getAdminGroup()`.

## Control Flow
The servlet container invokes `init()` through the webapp listener, then HttpFS resource/filter classes use `HttpFSServerWebApp.get()` to access configuration and services. On shutdown, `destroy()` tears down metrics before parent services.

## State and Persistence Behavior
Singleton and metrics references are process-local. No persistent state is written. Runtime metrics are registered with Hadoop's metrics system.

## Dependencies and Integration Points
It integrates with Ozone's `ServerWebApp`, `FileSystemAccess`, Hadoop metrics, `JvmPauseMonitor`, and `FSOperations` global buffer-size configuration. `HttpFSServer` uses the admin group for instrumentation authorization.

## Risks and Edge Cases
The singleton guard throws if multiple webapp instances initialize in the same process. `METRICS.updateAndGet()` keeps an existing metrics instance if one exists, which avoids duplicate registration but relies on proper `destroy()`. The pause monitor is started but not stored for explicit stop in this class.

## Test Signals
No direct test in this subset. Existing metrics tests elsewhere likely exercise `HttpFSServerMetrics`, but webapp lifecycle needs integration coverage.
