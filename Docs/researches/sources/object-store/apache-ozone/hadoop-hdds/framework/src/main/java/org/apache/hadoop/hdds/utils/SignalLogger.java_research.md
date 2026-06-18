# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/SignalLogger.java

## Purpose
`SignalLogger` logs UNIX termination-related signals before delegating to the previous signal handler. It helps operators distinguish normal shutdowns from signals such as SIGHUP, SIGINT, and SIGTERM.

## Important APIs and Types
The enum singleton `INSTANCE` exposes `register(Logger)`. Internal `Handler` implements `jnr.posix.SignalHandler`, installs itself with `POSIX.signal`, stores the previous handler or a default `System.exit` handler, and logs before delegation.

## Control Flow and State
`register` is one-shot: it throws if called more than once. It iterates the configured signal set, installs handlers, logs per-signal installation failures at info, and logs the final registered set. On signal receipt, `Handler.handle` logs the numeric signal and symbolic name, then invokes the previous handler.

## Persistence, Dependencies, and Integration
There is no persistence. It depends on JNR POSIX and HDDS audience/stability annotations. `HddsServerUtil.startupShutdownMessage` registers it for UNIX platforms during daemon startup.

## Risks and Test Signals
Because handler registration is process-global and one-shot, tests must isolate or reset process state carefully. Delegating to prior handlers is essential for normal shutdown behavior. Tests should cover repeated registration failure, handler installation failures, logging content, and non-UNIX startup paths that skip registration.
