<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java

Purpose: Implements OM HA member decommissioning. It validates the requested OM node ID and host address against configuration, optionally verifies all active OMs have reloaded decommission configuration, then asks the current OM leader to remove the node.

Important APIs and types: `OMAdminProtocolClientSideImpl`, `OzoneConfiguration`, `UserGroupInformation`, `OMNodeDetails`, `OMConfiguration`, `OmUtils`, `ConfUtils`, `OZONE_OM_ADDRESS_KEY`, `OZONE_OM_DECOMMISSIONED_NODES_KEY`, and nested `NodeIdOptions`/`HostnameOptions` with deprecated hidden aliases.

Control flow: `call()` obtains root configuration and user from `OMAdmin`, runs `verifyNodeIdAndHostAddress()`, and unless `--force` is set runs `verifyConfigUpdatedOnAllOMs()`. It then creates an HA admin proxy for the service ID, builds an `OMNodeDetails` for the target, invokes `decommission`, and prints success or failure before rethrowing errors.

State and persistence behavior: Local state stores the resolved target `InetAddress`, configuration, and user for the command invocation only. Persistent state is remote: OM Ratis membership and certificate/store metadata may be updated by the server. The config verification reads local and remote reloaded config but does not edit files.

Dependencies and integration points: Integrates Picocli arg groups, HA OM configuration naming, DNS resolution, OM admin protocol proxies for single OM and OM HA leader paths, and decommissioned-node config rollout. It is registered below `OMAdmin`.

Risks: DNS resolution and address equality are strict; host aliases can fail validation. The `--force` path skips a safety check and can decommission before every OM has reloaded config. The command prevents decommissioning the only active OM but cannot by itself preserve quorum in all operator workflows.

Test signals: Cover matching and mismatching node ID/host config, missing config keys, stale remote OM configs, `--force` bypass, deprecated `-nodeid` and `-hostname` options, success output, and IOException propagation from leader decommission.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/DecommissionOMSubcommand.java -->
