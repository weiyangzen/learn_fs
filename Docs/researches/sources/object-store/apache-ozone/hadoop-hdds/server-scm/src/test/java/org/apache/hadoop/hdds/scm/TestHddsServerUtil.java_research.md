# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/TestHddsServerUtil.java

Purpose: This JUnit suite verifies server-side SCM address parsing and bind-address behavior in `HddsServerUtil` and `SCMNodeInfo`. It focuses on the configuration rules datanodes and SCM use to choose SCM endpoints, including HA service-id configuration.

Important APIs and types: Tests use `OzoneConfiguration`, `SCMNodeInfo.buildNodeInfo`, `HddsServerUtil.getScmClientBindAddress`, `HddsServerUtil.getScmDataNodeBindAddress`, `HddsServerUtil.getSCMAddressForDatanodes`, `NetUtils.createSocketAddr`, `ConfUtils.addKeySuffixes`, and SCM config keys for client, datanode, names, service IDs, node IDs, addresses, and ports.

Control flow: `testGetScmDataNodeAddress` checks datanode endpoint precedence and port handling: client address fallback uses datanode default port, datanode address overrides client address, and datanode address port is respected. `testScmClientBindHostDefault` and `testScmDataNodeBindHostDefault` verify bind hosts default to `0.0.0.0`, bind-host override keys are respected, and ports come from the relevant advertised address. `testGetSCMAddresses` validates single and multiple `OZONE_SCM_NAMES` values, whitespace trimming, default ports, explicit ports, and invalid empty/hostname/port cases. `testGetSCMAddressesWithHAConfig` builds an HA service with three nodes and verifies the datanode address list from suffixed keys.

State and persistence behavior: There is no filesystem persistence. State is per-test `OzoneConfiguration`. The suite asserts computed `InetSocketAddress` values and exception behavior.

Dependencies and integration points: The tests protect address contracts used by datanodes connecting to SCM, SCM RPC bind behavior, and HA configuration parsing. They complement `TestHddsServerUtils`, which covers fallback and directory utilities in adjacent helpers.

Risks: Address parsing tests can be sensitive to `InetSocketAddress.getHostName` vs `getHostString` behavior. Invalid hostname validation depends on utility semantics. HA tests assume order-insensitive address collection and remove expected host:port strings from a list.

Test signals: Exact host and port assertions, thrown `IllegalArgumentException` for malformed configuration, bind host defaults, datanode override precedence, and complete HA node address coverage are the main regression signals.
