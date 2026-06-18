# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/VersionedDatanodeFeatures.java

Purpose: centralizes datanode behavior switches controlled by finalized HDDS layout features.

Important APIs and functions: `initialize` stores the process-wide `HDDSLayoutVersionManager`; `isFinalized` returns true when no manager is installed, or when the feature is allowed. `SchemaV2.chooseSchemaVersion` returns schema v2 after `DATANODE_SCHEMA_V2`, otherwise v1. `ScmHA.chooseContainerPathID` chooses cluster ID after SCM HA finalization or if the cluster-ID directory already exists; otherwise it requires exactly one pre-finalization directory and returns that name. `ScmHA.upgradeVolumeIfNeeded` invokes SCM HA volume upgrade when finalized but the cluster-ID path is missing. `SchemaV3.chooseSchemaVersion` returns schema v3 only when the feature is finalized and the datanode config enables it, otherwise defers to Schema V2.

Control flow and state: `versionManager` is static mutable global state, with null treated as latest version for tests. Feature methods are pure except `upgradeVolumeIfNeeded`, which may mutate the filesystem through the SCM HA action.

Dependencies and integration: used by container creation, volume path selection, upgrade actions, and `OzoneContainer` startup.

Risks and test signals: global manager state can leak between tests. Tests should reset/initialize manager, verify pre/post-finalization schema choices, SCM HA path selection for cluster/SCM directories, invalid multi-directory errors, disabled Schema V3 fallback, and upgrade-on-demand behavior.
