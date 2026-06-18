# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerVolumeCalculation.java

Purpose: Shared utility for immutable-ish volume usage snapshots and disk balancer utilization calculations.

Important APIs and types: Provides `getVolumeUsages`, `getIdealUsage`, `calculateVolumeDataDensity`, `computeUtilization`, `newVolumeFixedUsage`, and nested `VolumeFixedUsage` containing an `HddsVolume`, a fixed usage snapshot, effective used bytes, utilization, and usable-space calculation.

Control flow: `getVolumeUsages` snapshots each active volume and applies delta-map adjustments. `getIdealUsage` sums capacities and effective-used bytes, validating non-negative and not-over-capacity values. Density sums absolute deviations from ideal usage for positive-capacity volumes. Effective usage is filesystem used plus committed bytes plus required/delta bytes.

State and persistence: Stateless utility. `VolumeFixedUsage` captures a point-in-time usage snapshot from `HddsVolume.getCurrentUsage`.

Dependencies and integration points: Used by `DiskBalancerService` for status and bytes-to-move calculations and by `DefaultContainerChoosingPolicy` for selection. Depends on `VolumeUsage.getUsableSpace` for destination viability.

Risks: `newVolumeFixedUsage` asserts every `StorageVolume` is an `HddsVolume`; callers must not pass metadata or DB volume sets. Negative deltas can make effective-used negative and trigger exceptions. `calculateVolumeDataDensity` catches exceptions and returns `-1.0`, while `getIdealUsage` throws. Tests should cover zero-capacity volumes, delta effects, invalid negative/effective-over-capacity states, and consistency between status and policy calculations.
