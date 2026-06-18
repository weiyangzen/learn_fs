# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHANodeDetails.java

Purpose: Loads and holds local and peer SCM node configuration for HA clusters, including Ratis, gRPC, RPC, client, block, and datanode addresses.

Important APIs and types: `loadDefaultConfig`, `loadSCMHAConfig`, `getHASCMNodeDetails`, `getLocalNodeDetails`, and `getPeerNodeDetails`. It uses `SCMNodeDetails` as the node value object and applies node-specific config suffixes through `ConfUtils`.

Control flow: HA loading selects service ids from `ozone.scm.default.service.id` or `ozone.scm.service.ids`, iterates configured SCM node ids, resolves per-node RPC/Ratis/gRPC settings, identifies the local address, accumulates peers, sets node-specific keys, and returns local-plus-peer details. Missing node lists or SCM addresses raise configuration exceptions; no HA address falls back to default config.

State and persistence behavior: No persistence. It mutates the provided `OzoneConfiguration` by applying local node-specific overrides.

Dependencies and integration points: Used during SCM startup, Ratis peer creation, inter-SCM gRPC snapshot downloads, and command/bootstrap code.

Risks and test signals: Local-node detection is sensitive to DNS/FQDN resolution and multiple matching addresses. Tests should cover default mode, missing node ids, unresolved but flexible FQDNs, duplicate local matches, per-node port fallback, and peer list construction.
