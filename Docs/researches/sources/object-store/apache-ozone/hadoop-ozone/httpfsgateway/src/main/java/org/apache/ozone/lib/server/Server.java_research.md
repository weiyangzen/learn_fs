# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/lib/server/Server.java

## Purpose
`Server` is the HttpFS service container. It owns server directories, configuration loading, log4j initialization, service instantiation, dependency ordering checks, status transitions, and shutdown.

## Important APIs, types, and functions
Key configuration names are `services`, `services.ext`, and `startup.status`. Constructors validate absolute home/config/log/temp directories. `init()` verifies directories, loads build metadata, initializes logging and configuration, loads/deduplicates services, initializes and post-initializes them, then sets startup status. `setStatus()` notifies services, `get(Class<T>)` retrieves services, `setService()` programmatically replaces a service, and `destroy()` tears services down in reverse order. `Status` defines `UNDEF`, `BOOTING`, `HALTED`, `ADMIN`, `NORMAL`, `SHUTTING_DOWN`, and `SHUTDOWN`.

## Control flow
Initialization moves from `UNDEF` to `BOOTING`, loads defaults from `name-default.xml`, overlays site config or a supplied config, injects defaults, applies matching system properties, and uses Hadoop `Configuration#getClasses` to instantiate services. Duplicate service interfaces are resolved with last-one-wins semantics. Dependency checks require dependencies to have already initialized.

## State and persistence behavior
The server stores a mutable `Configuration`, lifecycle status, and a `LinkedHashMap<Class, Service>`. It reads XML/properties files and watches external log4j config if present, but does not persist server state itself.

## Dependencies and integration points
It integrates Hadoop configuration, `ConfigRedactor`, log4j/reload4j, `ConfigurationUtils`, `Check`, and all `Service` implementations. `ServerWebApp` binds this lifecycle to servlet context events.

## Risks and edge cases
Service instantiation uses deprecated no-arg reflection and raw class casts. `destroy()` calls `ensureOperational()`, so shutdown from non-operational states can throw. Status-change callback failures destroy the whole server. Missing classpath resources can surface as runtime or server exceptions.

## Test signals
`TestHttpFSMetrics` initializes `HttpFSServerWebApp`, replaces `FileSystemAccess`, and destroys the server, exercising config loading, service wiring, and programmatic replacement indirectly.
