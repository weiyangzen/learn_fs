# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestReservedVolumeSpace.java

## Purpose
Tests reserved capacity calculation from percentage and explicit per-volume configs, invalid config fallback/errors, symlink canonicalization, and minimum free space calculation.

## Important APIs, Types, And Functions
Uses `VolumeUsage.getReservedInBytes`, `realUsage`, `getCurrentUsage`, reserved-space config keys, `DatanodeConfiguration.getMinFreeSpace`, and `HddsVolume.Builder.conf`.

## Control Flow
Tests build volumes with default, percent, explicit path, mismatched path, invalid unit, invalid percent, invalid pair format, and symlink configurations. The min-free-space test verifies absolute-vs-percent max selection.

## State And Persistence
Temporary folders and a symlink are created. Reserved-space state is derived from configuration on `VolumeUsage`.

## Dependencies And Integration Points
Uses Ozone configuration parsing, `StorageUnit`, `ConfigurationException`, mock usage factories, and canonical filesystem paths.

## Risks And Edge Cases
Symlink creation can be platform-sensitive. Parser behavior changes may affect whether invalid config falls back or throws.

## Test Signals
Reserved byte equality, capacity reduction, thrown `ConfigurationException`, and min-free-space equality validate the contract.
