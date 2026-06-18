<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java

## Purpose

`VersionEndpointTask` performs the initial SCM GETVERSION RPC for an endpoint. For active SCM endpoints it validates SCM/cluster IDs, checks and prepares datanode storage volumes, starts container services with the cluster ID, then advances the endpoint to registration. The complete 136-line file was read.

## Important APIs, Types, and Functions

The class implements `Callable<EndpointStateMachine.EndPointStates>`. Its constructor receives `EndpointStateMachine`, `ConfigurationSource`, and `OzoneContainer`. `call()` runs the version flow. `checkVolumeSet(MutableVolumeSet, String, String)` validates each `StorageVolume` through `StorageVolumeUtil.checkVolume`.

## Control Flow

`call` locks the endpoint and only executes when state is GETVERSION. It calls SCM `getVersion(null)`, stores the parsed `VersionResponse` in the endpoint, and for non-passive endpoints extracts `SCM_ID` and `CLUSTER_ID`. Both values are required. It checks DB volumes first, then HDDS data volumes, failing individual volumes through the `MutableVolumeSet` if consistency checks fail. If all volumes in a set fail, it throws `DiskOutOfSpaceException`. After volume checks, it starts `OzoneContainer` with the cluster ID and advances the endpoint to its next state. Disk out-of-space or bind failures put the endpoint into SHUTDOWN; IOExceptions are logged for retry.

## State and Persistence Behavior

This task can create/format volume `VERSION` files, working directories, cluster/SCM compatibility links, and temporary directories through `StorageVolumeUtil`. It also starts container services, mutates endpoint version and state, and resets missed heartbeat count.

## Dependencies and Integration Points

It integrates with SCM endpoint RPC, `VersionResponse`, `OzoneContainer`, both DB and data `MutableVolumeSet`s, `StorageVolumeUtil`, and `DiskChecker.DiskOutOfSpaceException`. Passive endpoints skip volume checks and container start.

## Risks and Edge Cases

Volume checks run under a write lock and may mark volumes failed while iterating. A completely failed volume set shuts down the endpoint. Passive endpoints do not validate local storage in this path. `Objects.requireNonNull` on SCM/cluster IDs turns missing version values into runtime failures rather than a protocol result.

## Test Signals

Tests should cover active versus passive behavior, successful volume formatting/start, failed individual volume handling, all-volumes-failed shutdown, GETVERSION skipped in other endpoint states, missing SCM/cluster values, and BindException/DiskOutOfSpace shutdown behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/states/endpoint/VersionEndpointTask.java -->
