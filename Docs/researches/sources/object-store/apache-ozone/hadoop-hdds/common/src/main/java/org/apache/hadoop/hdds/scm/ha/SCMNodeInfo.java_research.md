# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMNodeInfo.java

## Purpose
Builds immutable SCM node endpoint information from configuration for clients, OzoneManager, and admin commands. It supports HA service/node-suffixed config and non-HA fallback config.

## Important APIs, Types, And Functions
`buildNodeInfo(ConfigurationSource)` is the main API. `getPort` resolves node-specific address-port deprecations and port keys. `buildAddress` joins host and port. Getters expose service ID, node ID, block client, SCM client, security, and datanode addresses.

## Control Flow
If `HddsUtils.getScmServiceId` returns an HA service, node IDs are required. For each node, the base SCM address is required and endpoint ports are resolved from address keys or suffixed/global port keys. Without HA, dummy service/node IDs are used and hostnames fall back from client address to `ozone.scm.names`.

## State And Persistence
Instances are immutable snapshots of external configuration. No state is written.

## Dependencies And Integration Points
Depends on `ConfigurationSource`, `HddsUtils`, `ConfUtils`, SCM config keys, and Ozone dummy constants. Integrated by SCM clients, OM, admin commands, and HA discovery.

## Risks And Test Signals
`buildAddress` appends ports to the base address even if it already contains a port in HA path, relying on host extraction in config. Non-HA can produce null addresses. Tests should cover HA missing nodes/address, suffixed ports, deprecated address-port parsing, and non-HA fallbacks.
