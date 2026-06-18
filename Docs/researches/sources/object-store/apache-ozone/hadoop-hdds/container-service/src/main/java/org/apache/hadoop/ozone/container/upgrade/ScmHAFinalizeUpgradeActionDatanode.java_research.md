# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/upgrade/ScmHAFinalizeUpgradeActionDatanode.java

Purpose: finalizes datanode volume layout for SCM HA by ensuring cluster-ID paths exist, often through symlinks to older SCM-ID directories.

Important APIs and functions: annotated for `SCM_HA`. `execute` iterates data volumes under the volume-set write lock and calls `upgradeVolume` for `HddsVolume`s, failing the volume if upgrade returns false. `upgradeVolume` validates cluster ID, lists storage subdirectories, skips unformatted volumes, creates a symlink from `<volume>/<clusterID>` to the sole old directory when needed, accepts already-correct layouts, and rejects inconsistent multi-directory layouts without cluster ID.

Control flow and state: the upgrade mutates filesystem layout, not in-memory container state. It returns boolean success so callers can mark failed volumes for later handling.

Dependencies and integration: coordinated with `VersionedDatanodeFeatures.ScmHA.chooseContainerPathID` and `upgradeVolumeIfNeeded`.

Risks and test signals: symlink creation portability and inconsistent directory detection are high risk. Tests should cover null cluster ID, unformatted volume, one old SCM-ID directory, existing cluster-ID directory, multi-directory with/without cluster ID, IO failure, and volume failure marking.
