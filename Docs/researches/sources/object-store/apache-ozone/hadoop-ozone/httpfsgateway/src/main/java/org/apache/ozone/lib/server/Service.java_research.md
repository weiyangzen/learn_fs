# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Service.java

## Purpose
`Service` defines the lifecycle contract for components managed by `Server`.

## Important APIs, types, and functions
Implementations provide `init(Server)`, `postInit()`, `destroy()`, `getServiceDependencies()`, `getInterface()`, and `serverStatusChange(oldStatus, newStatus)`.

## Control flow
`Server` constructs services, validates dependencies, calls `init`, registers by interface, calls `postInit`, notifies status changes, and destroys in reverse order.

## State and persistence behavior
The interface owns no state. Implementations may own resources such as schedulers, metrics, or filesystem caches.

## Dependencies and integration points
The `getInterface()` return value is the service key used by `Server#get(Class)`, enabling concrete services to be replaced by extensions.

## Risks and edge cases
Raw `Class[]` and `Class` returns provide little compile-time safety. Incorrect `getInterface()` values can hide services or break dependency lookup.

## Test signals
`TestHttpFSMetrics` exercises service replacement and lookup via the `FileSystemAccess` interface.
