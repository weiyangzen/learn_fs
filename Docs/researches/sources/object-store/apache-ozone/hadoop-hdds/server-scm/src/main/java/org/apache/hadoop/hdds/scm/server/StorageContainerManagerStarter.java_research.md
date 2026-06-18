# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerStarter.java

Purpose: This class is the picocli-based entry point for `ozone scm`. It handles normal daemon startup and subcommands for generating a cluster ID, initializing SCM storage, and bootstrapping an SCM into an HA ring.

Important APIs and types: The class extends `GenericCli` and implements `Callable<Void>`. It defines `main`, `call`, `generateClusterId`, `initScm`, `bootStrapScm`, `startScm`, and `commonInit`. The nested `SCMStarterHelper` implements `SCMStarterInterface` using production SCM methods and registers a shutdown hook with `ShutdownHookManager`.

Control flow: `main` disables JVM network address cache if configured, then runs the CLI with a production receiver. Each command calls `commonInit`, which loads `OzoneConfiguration`, extracts original arguments, and emits the startup/shutdown banner. The default `call` starts SCM through the receiver. `--init` passes the optional `--clusterid` and throws if the receiver returns false. `--bootstrap` similarly throws on false. `--genclusterid` prints a newly generated cluster ID.

State and persistence behavior: The starter itself persists no state. Its receiver can create VERSION files, bootstrap HA storage, start the SCM service, and add a shutdown hook. The production start path keeps the `StorageContainerManager` instance alive and shuts it down on JVM exit.

Dependencies and integration points: It connects CLI parsing, version reporting, server banner logging, network cache behavior, SCM init/bootstrap/start operations, and shutdown hooks. Tests can inject a fake receiver to isolate CLI behavior from SCM construction.

Risks: The subcommand names use flag-like command names (`--init`, `--bootstrap`, `--genclusterid`), so parser behavior is unusual and should be tested. The shutdown hook calls both `stop` and `join`; if `stop` hangs or partially fails, process shutdown can be delayed. Exceptions during `call` are logged and rethrown.

Test signals: `TestStorageContainerManagerStarter` should verify receiver invocation, cluster ID output, false-result failures, propagated exceptions, startup banner initialization, and shutdown hook registration for normal start.
