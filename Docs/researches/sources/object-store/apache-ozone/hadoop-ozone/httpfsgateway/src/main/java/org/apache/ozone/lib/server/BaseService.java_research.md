# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/BaseService.java

## Purpose
`BaseService` is the convenience superclass for HttpFS services managed by `Server`. It extracts service-scoped configuration and supplies no-op lifecycle defaults.

## Important APIs, types, and functions
`init(Server)` is final and captures the owning server, derives a prefix of `serverPrefix.servicePrefix.`, copies matching resolved configuration entries into an unprefixed `serviceConfig`, and calls abstract `init()`. It also provides `postInit()`, `destroy()`, `getServiceDependencies()`, `serverStatusChange()`, `getServer()`, `getServiceConfig()`, and `getPrefixedName()`.

## Control flow
Service implementations only override protected `init()` and optional lifecycle hooks. Server initialization calls `init(Server)` once, then calls `postInit()` after all services are registered.

## State and persistence behavior
State is in-memory references to service prefix, owner server, and a per-service Hadoop `Configuration`. No durable writes occur.

## Dependencies and integration points
It depends on `ConfigurationUtils.resolve` to expand inline config values before trimming prefixes. Implementations include instrumentation, scheduler, groups, and filesystem access services.

## Risks and edge cases
The final `init(Server)` means subclasses cannot customize prefix extraction. Misconfigured prefixes silently omit properties from `serviceConfig`, leaving defaults active. The raw `Class[]` dependency API lacks type safety.

## Test signals
Indirect signals appear when `Server` initializes configured services and when `FileSystemAccessService`, `SchedulerService`, and `GroupsService` read their scoped settings.
