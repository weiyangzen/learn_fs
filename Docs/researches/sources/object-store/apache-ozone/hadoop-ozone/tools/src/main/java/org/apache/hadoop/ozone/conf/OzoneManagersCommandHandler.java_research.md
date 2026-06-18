# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneManagersCommandHandler.java

## Purpose
Subcommand handler for `ozone getconf ozonemanagers` and `-ozonemanagers`, printing configured OM host names.

## Important APIs, types, and functions
Implements `Callable<Void>`, uses parent `OzoneGetConf`, `OzoneConfiguration.of`, `OmUtils.isServiceIdsDefined`, `getOmHAAddressesById`, and `OmUtils.getOmAddress`.

## Control flow
On call, it wraps the parent config as a `ConfigurationSource`. If OM service IDs are defined, it flattens all HA service address collections and prints each host name. Otherwise it prints the singleton OM address host name.

## State and persistence behavior
Read-only configuration inspection; no persistence.

## Dependencies and integration points
Connects the getconf CLI to OM HA/single-node address parsing in `OmUtils`.

## Risks and edge cases
For HA services, it prints all service addresses without filtering to a selected service. Host names are printed without ports, and unresolved/empty configurations may produce blank output or upstream exceptions.

## Test signals
Tests set a service ID without node addresses and assert empty output for both alias forms, confirming current handling of incomplete HA config.
