# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneHAClusterImpl.java

## Purpose

`MiniOzoneHAClusterImpl` is the in-process HA variant of Ozone's test cluster. It extends `MiniOzoneClusterImpl` and builds a single-JVM cluster containing multiple Ozone Managers, multiple Storage Container Managers, and datanodes. It exists primarily for integration and failure-mode tests that need OM HA, SCM HA, bootstrapping, leadership transfer, and active/inactive node lifecycle control.

## Important APIs and Types

- `MiniOzoneHAClusterImpl` exposes cluster accessors such as `getOzoneManager()`, `getOzoneManager(String)`, `getStorageContainerManagersList()`, `getSCM(String)`, `getOMLeader()`, `waitForLeaderOM()`, `getScmLeader(boolean)`, and active/inactive checks.
- Lifecycle APIs include `restartOzoneManagersWithConfigCustomizer`, `restartOzoneManager`, `shutdownOzoneManager`, `restartStorageContainerManager`, `stopOzoneManager`, `stopSCM`, `startInactiveOM`, and `startInactiveSCM`.
- HA expansion APIs include `bootstrapOzoneManager`, `bootstrapSCM`, `addNewOMToConfig`, `addNewSCMToConfig`, `updateOMConfigs`, and `updateSCMConfigs`.
- `Builder` configures OM/SCM counts, service IDs, active counts, low Ratis timeouts, HA address keys, metadata directories, and service startup.
- `MiniOzoneHAService<Type>` is the shared active/inactive registry used by `OMHAService` and `SCMHAService`.
- `ExitManagerForOM` converts an OM test-time exit into a cluster stop of that OM and an `IOException`.

## Control Flow

The builder validates active counts, fills defaults, enables mini-cluster metrics/store modes, initializes generic cluster configuration, adjusts OM Ratis timeouts, creates SCM service first, creates OM service second, creates datanodes, constructs the cluster, starts registered services, optionally starts datanodes, and prepares the builder for reuse. HA service creation loops retry on `BindException`; each retry stops any partially created service instances and re-runs port allocation.

For OM HA, `initOMHAConfig` writes service IDs and node lists into configuration, allocates RPC/HTTP/HTTPS/Ratis ports for each node, initializes a per-node metadata directory, calls `OzoneManager.omInit`, creates each OM, installs clients, starts only the first `numOfActiveOMs`, and records the rest as inactive. For SCM HA, `initSCMHAConfig` writes SCM service and node lists, sets the primordial SCM, allocates node-specific RPC/HTTP/HTTPS/security/Ratis/datanode/block/client/gRPC ports, initializes the first SCM with `scmInit`, bootstraps later SCMs with `scmBootstrap`, creates SCM instances, adjusts the healthy pipeline safe-mode threshold, starts active SCMs, and configures datanode addresses from active SCMs.

Leader lookup is polling-based. `getOMLeader` scans active OMs and returns a single leader only if exactly one reports `isLeaderReady`; multiple leaders return `null` so callers retry. `waitForLeaderOM` and `getScmLeader(true)` use `GenericTestUtils.waitFor` with the cluster readiness timeout. Leadership transfer removes the current leader from the list, picks the first remaining OM, calls `transferLeadership`, and waits until `getOMLeader()` reports a different node.

OM bootstrapping first freezes reload behavior for tests, captures the current leader snapshot index, builds a new configuration with a new node in the OM node list, optionally pushes that configuration to active OMs, creates the new OM in `BOOTSTRAP` or `FORCE_BOOTSTRAP` mode, registers it inactive, starts it, updates the cluster configuration, waits for the new OM's Ratis snapshot index to catch up, and optionally verifies peer-list propagation. SCM bootstrapping mirrors that flow with SCM-specific configuration and SCM Ratis snapshot checks.

## State and Persistence

Cluster state is held in the inherited configuration, `clusterMetaPath`, `OMHAService`, and `SCMHAService`. Each OM and SCM gets its own metadata subdirectory under the cluster path or node-specific path. HA service state is in-memory maps/lists tracking all services plus active and inactive subsets; this registry is not thread-safe and is suitable for test control paths, not production synchronization.

Persistent state belongs to the embedded services themselves: OM metadata DB/Ratis state under per-node `OZONE_METADATA_DIRS`, SCM metadata/Ratis state under per-node SCM directories, and datanode state from the parent cluster. Bootstrap methods mutate both service process state and configuration state; if a bind failure happens after active service configs were updated, the code resets existing service configurations to the previous cluster config.

## Dependencies and Integration Points

The class integrates with `OzoneManager`, `StorageContainerManager`, Ratis, `HddsTestUtils`, `SCMConfigurator`, `DatanodeStoreCache`, `DefaultMetricsSystem`, `OzoneClientFactory`, `OzoneManagerRatisServer`, `ConfUtils`, HDDS/OM/SCM config keys, `GenericTestUtils`, and port allocation helpers. It relies on the parent `MiniOzoneClusterImpl` for datanode creation, common service startup, client wiring, stopping OMs, and overall cluster shutdown.

## Risks and Edge Cases

There is heavy reliance on dynamically allocated local ports; retry loops handle bind conflicts but can spin until allocation succeeds. `MiniOzoneHAService` creates `services` from `HashMap.values()`, so service ordering can be non-deterministic despite index-based accessors. Some lifecycle calls manipulate active/inactive lists directly and assume single-threaded test usage. `bootstrapSCM` places readiness/config-update waits inside the retry loop after the catch block, which means a successful `break` exits before those waits; that is a control-flow risk worth verifying against tests. `waitForConfigUpdateOnActiveSCMs` checks `scm.doesPeerExist(scm.getScmId())` for each active SCM instead of the new SCM node ID, which may be intentional or a bug. `transferOMLeadershipToAnotherNode` mutates the list returned by `getOzoneManagersList`, so it can remove the current leader from cluster state if that list is the live backing list.

## Test Signals

This file is itself test infrastructure. The strongest signals are expected from HA mini-cluster integration tests that exercise bind retry, OM/SCM leader election, active/inactive startup, restart, bootstrap, force bootstrap, listener OMs, SCM bootstrap, peer propagation, and shutdown. Risky areas need tests that assert service ordering, no accidental list mutation during leadership transfer, post-bootstrap peer visibility, and SCM bootstrap wait behavior.
