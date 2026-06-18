# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerConfiguration.java

## Purpose
Tests OM configuration parsing for single-node and HA services, including address defaults, peer/ratis address derivation, unresolved hosts, invalid HA configs, and multiple service IDs.

## Important APIs, types, and functions
- Builds `MiniOzoneCluster` without datanodes from an `OzoneConfiguration` rooted in a temp metadata directory.
- Uses `OMConfigKeys`, `ConfUtils.addKeySuffixes`, `OZONE_OM_SERVICE_IDS_KEY`, `OZONE_OM_NODES_KEY`, `OZONE_OM_ADDRESS_KEY`, and `OZONE_OM_RATIS_PORT_KEY`.
- Inspects `OzoneManager.getOmRpcServerAddr`, `getPeerNodes`, `getOMServiceId`, `getOmRatisServerState`, `OzoneManagerRatisServer.getRaftGroup`, and `RaftPeer` addresses.

## Control flow
Each test prepares a different configuration and then calls `startCluster`. Positive tests assert local address binding, default RPC/Ratis ports, selected local OM node id, peer count, peer addresses, unresolved peer metadata, and service ID selection. Negative tests run startup under disabled logs and expect `OzoneIllegalArgumentException` for no local matching address, missing node list, or missing OM addresses.

## State and persistence behavior
The cluster writes metadata under a temp path, but the tested state is runtime configuration materialized into OM node details and Ratis peer groups. No long-lived metadata content is inspected.

## Dependencies and integration points
This file sits between configuration keys, HA node discovery, NetUtils local-address checks, MiniOzoneCluster construction, OM Ratis server setup, and Ratis peer configuration.

## Risks and edge cases
Tests use dummy IPs and `0.0.0.0` to force local-node detection. Address resolution behavior can vary by environment, so unresolved-host assertions deliberately check `isHostUnresolved` and null inet addresses. Exact exception messages are part of the contract.

## Test signals
Signals include cluster readiness, Ratis lifecycle `RUNNING`, expected `RaftPeer` counts and addresses, selected service/node ids, unresolved peer flags, and expected startup exceptions/messages for invalid configs.
