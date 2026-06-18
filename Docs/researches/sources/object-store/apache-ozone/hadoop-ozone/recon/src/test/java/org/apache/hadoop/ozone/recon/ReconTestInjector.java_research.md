# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/ReconTestInjector.java

## Purpose
`ReconTestInjector` wraps Guice setup for Recon unit and integration tests. It lets tests compose a temporary `OzoneConfiguration`, optional Recon SQL schema, OM/SCM service instances, container metadata managers, and extra bindings without repeating module wiring.

## Important APIs and functions
The outer class stores configured components and exposes `getInstance`/`getInjector`. `setupInjector` creates a base `AbstractModule` binding `OzoneConfiguration`, supplied OM/SCM providers, optional container DB managers, and caller-provided instance/class/inherited bindings. `getTestOzoneConfiguration` points Recon DB, OM snapshot DB, and SCM DB dirs at the temp directory and sets test datanode/prometheus endpoints. The nested `Builder` exposes fluent methods such as `withReconSqlDb`, `withOmServiceProvider`, `withReconOm`, `withReconScm`, `withContainerDB`, `addBinding`, `addModule`, and `build`.

## Control flow, state, and persistence
`build` calls `setupInjector`, which optionally constructs `AbstractReconSqlDBTest`, appends SQL modules, creates the Guice injector, and creates SQL schema after injection. Persistence is limited to temporary DB paths passed by tests.

## Dependencies and integration points
The class integrates Guice, Recon SQL DB test modules, SCM facade classes, Recon metadata manager implementations, and service-provider interfaces. It is central to the endpoint tests in this subset.

## Risks and edge cases
Raw `Class` maps/sets lose generic type safety. Optional manager binding means missing dependencies fail at injection time rather than builder time. `tmpDir` is required only by a runtime precondition. Binding default container DB implementations under `withContainerDB` can create substantial RocksDB/SQL state that must be cleared by tests.

## Test signals
No direct tests target this builder, but every endpoint test using `new ReconTestInjector.Builder(...).build()` validates its wiring. Failures usually surface as Guice creation errors or missing schema/table errors.
