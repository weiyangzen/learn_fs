# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconServer.java

## Purpose
`ReconServer` is the CLI entry point and lifecycle owner for the Recon service. It constructs the injector, initializes storage/security/schema, starts HTTP and metadata services, runs layout finalization, and coordinates shutdown.

## Important APIs, Types, And Functions
It extends `GenericCli` and implements `Callable<Void>`. Key methods are `call`, `start`, `stop`, `join`, `initializeCertificateClient`, `saveNewCertId`, `terminateRecon`, `loginReconUserIfSecurityEnabled`, `createReconAdmins`, `isAdmin`, and visible-for-testing accessors.

## Control Flow
`call()` loads configuration, registers it in `ConfigurationProvider`, computes Recon admins, creates Guice modules, sets the servlet injector, initializes storage and certificates when secure, creates schema, enables safe mode, obtains services, starts services, finalizes layout features, registers task metrics, and installs a shutdown hook. On initialization errors it logs and updates health based on missing components.

## State And Persistence
Runtime fields hold injector, HTTP server, metadata managers, service providers, storage config, certificate client, metrics, admins, and `isStarted`. Persistent side effects include Recon VERSION/storage initialization, certificate serial persistence, SQL schema DDL, layout version updates, and DB/provider state.

## Dependencies And Integration Points
It integrates CLI, Guice, Jetty, OM/SCM providers, Recon DB, schema manager, safe mode, metrics, security login, certificate recovery, feature flags, and shutdown hooks.

## Risks
Some initialization exceptions are caught and logged without terminating, so partial startup is possible. `start()` sets `isStarted` before all services start. `updateAndLogReconHealthStatus()` assumes `injector` is available. Security login failures are logged in helper code and may allow later failures rather than immediate abort.

## Test Signals
Tests should exercise normal lifecycle, stop idempotency, secure and insecure startup, admin resolution, health updates after component failures, schema-before-upgrade ordering, metrics register/unregister, and shutdown cleanup.
