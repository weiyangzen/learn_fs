# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/StorageContainerManagersCommandHandler.java

## Purpose
Subcommand handler for `ozone getconf storagecontainermanagers`, printing SCM host names used by clients.

## Important APIs, types, and functions
Implements `Callable<Void>`, uses `HddsUtils.getScmAddressForClients`, parent `OzoneGetConf`, and `OzoneConfiguration.of`.

## Control flow
On invocation, it resolves client-facing SCM addresses from the current config and prints the host name for each `InetSocketAddress`.

## State and persistence behavior
Read-only config lookup; no persistence.

## Dependencies and integration points
Connects getconf output to HDDS SCM client address resolution.

## Risks and edge cases
Ports are omitted. Multiple SCM addresses print one per line. Invalid SCM configuration errors are delegated to `HddsUtils`.

## Test signals
Tests set `ozone.scm.names` to localhost and assert both alias forms print `localhost`.
