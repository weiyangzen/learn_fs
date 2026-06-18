# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/hdds/scm/VersionInfo.java

## Purpose
Small version registry for SCM metadata in this module.

## Important APIs, Types, And Functions
Static APIs `getAllVersions()` and `getLatestVersion()` expose immutable copies from a private `VERSION_INFOS` array. Instance getters expose description and version. `DESCRIPTION_KEY` names the metadata key.

## Control Flow
Callers request all versions or the latest; the current implementation contains a single version with numeric version 1.

## State And Persistence
Version entries are immutable private objects. The array is cloned for callers to avoid direct mutation.

## Dependencies And Integration Points
Related to layout/version tracking code in HDDS/SCM, though this class is minimal in the subset.

## Risks
Adding versions requires preserving ascending order because `getLatestVersion()` returns the last array element. The class name overlaps with other HDDS version info types.

## Test Signals
Signals include tests that latest version is the expected final element and callers cannot mutate the internal array.
