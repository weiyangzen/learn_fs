# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/HddsServerUtil.java

## Purpose
`HddsServerUtil` is a broad server-side utility class for Ozone/HDDS daemons. It centralizes RPC protocol registration, SCM/Recon bind address resolution, heartbeat/dead-node timing validation, datanode storage directory handling, security/secret-key client creation, metrics initialization, DB checkpoint streaming, startup/shutdown logging, thread-pool resizing, and SCM address discovery.

## Important APIs and Types
Important methods include `addPBProtocol`, `getValidInetsForCurrentHost`, `isScopedOrMaskingIPv6Address`, `getScm*BindAddress`, `getReconDataNodeBindAddress`, heartbeat interval helpers, `getStaleNodeInterval`, `getDeadNodeInterval`, `getDatanodeStorageDirs`, `getDatanodeIdFilePath`, `getScmSecurityClient*`, `getSecretKeyClient*`, `initializeMetrics`, `writeDBCheckpointToStream`, `includeRatisSnapshotCompleteFlag`, `startupShutdownMessage`, `setPoolSize`, and `getSCMAddressForDatanodes`.

## Control Flow and State
Address helpers combine host and port config keys with defaults and return Hadoop `NetUtils` socket addresses. Timing helpers read durations and run them through `sanitizeUserArgs` to maintain minimum relationships between heartbeat, stale, and dead intervals. Checkpoint streaming lists the checkpoint directory, excludes requested filenames, tars each remaining file, and appends the Ratis completion flag. Startup logging also registers UNIX signal handlers and a shutdown hook.

## Persistence, Dependencies, and Integration
The class uses Hadoop RPC, Protobuf services, `DefaultMetricsSystem`, `JvmMetrics`, `CpuMetrics`, SCM HA node metadata, security failover providers, archive helpers, and `DBCheckpoint`. It is a key integration layer between server configuration, RPC endpoints, datanode/SCM/Recon discovery, certificate/secret-key services, and snapshot transfer.

## Risks and Test Signals
Network enumeration must not include loopback, wildcard, scoped IPv6, or prefix-length IPv6 addresses in certificate SANs. `getDatanodeStorageDirs` deliberately throws when required data dirs are absent, while DB dirs are optional. `setPoolSize` updates maximum/core pool sizes in different orders to preserve executor invariants. Tests should verify HA and legacy SCM address parsing, malformed host handling, checkpoint tar exclusion and completion flag inclusion, secret/security client UGI selection, and timing sanitation.
