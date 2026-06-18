<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java

## Purpose

`StorageVolumeUtil` provides common storage-volume helpers for VERSION file validation, volume UUID generation, volume consistency checks, failure scheduling, and typed volume list conversion. The complete 277-line file was read.

## Important APIs, Types, and Functions

Public APIs include `onFailure`, `getHddsVolumesList`, `getDbVolumesList`, `getVersionFile`, `generateUuid`, property validators for storage ID, cluster ID, datanode UUID, creation time, layout version, `getProperty`, and `checkVolume`. Constants include `VERSION_FILE` and storage ID prefix `DS-`.

## Control Flow

Validation helpers read required properties and throw `InconsistentStorageStateException` for missing, mismatched, future/negative creation time, or layout-version mismatch. `checkVolume` formats the volume if necessary, lists root files, chooses the correct working directory under the cluster ID or legacy SCM ID, upgrades SCM HA symlinks when needed, creates a working directory for first-use volumes, tolerates extra files only when a cluster ID directory exists, and creates volume-level temporary directories. Failures are logged and return false.

## State and Persistence Behavior

`checkVolume` may create or update VERSION files, working directories, SCM-HA compatibility symlinks, and tmp directories. `generateUuid` creates new storage IDs. `onFailure` schedules async volume checks through a mutable volume set.

## Dependencies and Integration Points

It integrates with `StorageVolume`, `HddsVolume`, `DbVolume`, `MutableVolumeSet`, `VolumeSet`, `HDDSVolumeLayoutVersion`, `VersionedDatanodeFeatures.ScmHA`, `OzoneConsts`, and startup `VersionEndpointTask` volume checks.

## Risks and Edge Cases

The root-file-count logic is sensitive to unexpected files in volume roots. Existing SCM-ID layouts depend on SCM HA feature helpers to choose and upgrade paths correctly. Typed list conversion uses unchecked casts. Invalid creation time depends on local system clock.

## Test Signals

Tests should cover property validation, mismatched cluster/datanode IDs, layout mismatch, first-format volume, legacy SCM ID layout before/after SCM HA finalization, extra root files with and without cluster dir, tmp-dir creation failure, failure scheduling, and typed list conversion assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/StorageVolumeUtil.java -->
