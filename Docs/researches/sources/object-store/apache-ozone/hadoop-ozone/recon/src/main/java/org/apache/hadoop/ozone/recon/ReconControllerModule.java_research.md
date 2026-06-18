# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconControllerModule.java

## Purpose
`ReconControllerModule` is the main Guice module for the Recon backend. It binds service implementations, persistence modules, Recon tasks, generated DAOs, RPC clients, and SQL datasource configuration.

## Important APIs, Types, And Functions
`configure()` binds core services such as `ReconHttpServer`, `ReconDBProvider`, metadata managers, OM/SCM providers, task controller, SCM facade, metrics factory, and optional chatbot module. Nested modules bind `ReconOmTask` implementations and generated jOOQ DAO constructors. Provider methods create an executor, `OzoneManagerProtocol`, `StorageContainerLocationProtocol`, and `DataSourceConfiguration`.

## Control Flow
Guice installs persistence, task, DAO, and optional chatbot bindings. DAO classes are bound reflectively to constructors accepting jOOQ `Configuration`. The datasource provider resolves `${ozone.recon.db.dir}`-style Derby URLs by computing the configured Recon DB directory.

## State And Persistence
The module itself holds the `ReconServer` instance. It configures persistent SQL access but does not write directly. The provided executor is a fixed five-thread pool.

## Dependencies And Integration Points
It integrates Guice, jOOQ, generated schema DAOs, OM/SCM RPC clients, Recon metadata managers, tasks, heatmap service, and chatbot feature bindings.

## Risks
Provider methods return null on OM protocol construction failure, which can defer errors into consumers. Reflective DAO binding logs missing constructors but continues. The fixed executor and hard-coded task multibindings can become bottlenecks or require updates when tasks are added.

## Test Signals
Injector creation tests should assert expected bindings, DAO constructor binding, datasource URL resolution, optional chatbot binding behavior, and provider behavior on bad RPC configuration.
