# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/servlet/ServerWebApp.java

## Purpose
`ServerWebApp` binds the `Server` lifecycle to a servlet container. It resolves directories and HTTP authority from system properties and starts/stops the server from servlet context events.

## Important APIs, types, and functions
The constructor reads `name.home.dir`, optional config/log/temp dir properties, and calls the `Server` constructor. `contextInitialized()` calls `init()` and wraps `ServerException` as `RuntimeException`. `contextDestroyed()` calls `destroy()`. `getAuthority()` lazily resolves `name.http.hostname` and `name.http.port`.

## Control flow
Directory resolution happens during construction. Servlet startup calls server initialization. Authority resolution is synchronized and cached after the first call.

## State and persistence behavior
State is the inherited server state and cached `InetSocketAddress`. It reads system properties but does not persist data.

## Dependencies and integration points
`HttpFSServerWebApp` subclasses this type and is configured as the listener in both web descriptors. The server process launcher must set system properties such as `httpfs.home.dir`.

## Risks and edge cases
Missing `home.dir`, `http.hostname`, or `http.port` properties fail early. `HOME_DIR_TL` exists but has no setter in this file, so normal resolution relies on system properties. Invalid hostnames or non-numeric ports fail authority resolution.

## Test signals
`TestHttpFSMetrics` sets `httpfs.home.dir`, creates `HttpFSServerWebApp`, initializes it, replaces a service, and destroys it, exercising this lifecycle.
