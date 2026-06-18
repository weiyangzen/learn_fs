# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/Storage.java

## Purpose

`Storage` is an abstract base for Ozone component storage directory state. It validates root/current/VERSION layout, creates or reads `StorageInfo`, and persists layout/cluster/node metadata. The complete 301-line source was read for this report.

## Important APIs, Types, and Functions

Constants include `STORAGE_DIR_CURRENT`, `STORAGE_FILE_VERSION`, and `CONTAINER_DIR`. Enum `StorageState` has `NON_EXISTENT`, `NOT_INITIALIZED`, and `INITIALIZED`. Key methods are constructors, getters for storage dir/state/node/cluster/creation/layout, setters for cluster/layout/first-upgrade-action layout, `getCurrentDir`, `getVersionFile`, `initialize`, `forceInitialize`, `persistCurrentState`, abstract `getNodeProperties`, and static `getInitLayoutVersion`.

## Control Flow

Construction computes storage state. If initialized, it reads `StorageInfo` from the VERSION file; otherwise it creates a new `StorageInfo` with cluster ID/default layout and component-specific node properties. `getStorageState` checks root existence, directory status, writability, VERSION presence, and emptiness of `current/` before allowing initialization. `initialize` creates `current/` and writes VERSION. `forceInitialize` rewrites VERSION if already initialized.

## State and Persistence Behavior

Persistent state is the `current/VERSION` properties file, written last as the validity marker for a storage directory. `StorageInfo` holds cluster ID, node type, creation time, layout version, and component properties. `persistCurrentState` rewrites the current metadata state.

## Dependencies and Integration Points

It depends on `StorageInfo`, `InconsistentStorageStateException`, `OzoneConfiguration`, `NodeType`, Hadoop `Time`, and Ozone config constants. OM, SCM, and datanode storage implementations extend it with node-specific properties.

## Risks and Edge Cases

`initialize` fails if `mkdirs` returns false, including if the directory was concurrently created. Root writability checks can be platform-dependent. Non-empty `current/` without VERSION is treated as inconsistent. `setClusterId` is forbidden after initialization. VERSION write failures can leave partially initialized directories.

## Test Signals

Tests should cover non-existent, non-directory, unwritable, initialized, empty current, and non-empty current states; initialize/forceInitialize/persist behavior; layout version setters; cluster ID restrictions; and config default layout selection.
