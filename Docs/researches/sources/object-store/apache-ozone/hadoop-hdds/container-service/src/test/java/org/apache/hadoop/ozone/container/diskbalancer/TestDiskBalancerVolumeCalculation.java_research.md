# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerVolumeCalculation.java

Purpose: validates defensive arithmetic in `DiskBalancerVolumeCalculation` and volume report utilization for empty, zero-capacity, and invalid volume-usage inputs.

Important APIs/types/functions: `DiskBalancerVolumeCalculation.getIdealUsage`, `calculateVolumeDataDensity`, `newVolumeFixedUsage`, `VolumeFixedUsage.getUtilization`, and `DiskBalancerService.buildVolumeReportProto`. The local `createVolume()` helper builds `HddsVolume` instances backed by `MockSpaceUsageSource.fixed()` and `MockSpaceUsageCheckFactory`.

Control flow: each test constructs one or more mock-backed volumes with synthetic capacity/available values, wraps them in `VolumeFixedUsage`, and checks calculations or expected exceptions. Zero-capacity tests assert zero ideal usage/utilization and that zero-capacity volumes do not affect density. Negative capacity/effective-used and effective-used-greater-than-capacity tests assert `IllegalArgumentException` with exact messages.

State and persistence behavior: the file uses `@TempDir` to give each `HddsVolume` a filesystem root, but no durable container state is written. The significant state is the fixed space usage snapshot captured in each `HddsVolume` and optional effective-used adjustment map.

Dependencies and integration points: integrates disk balancer math with HDDS volume usage abstractions and the service's volume-report protobuf builder. It depends on mock space usage plumbing rather than real disk accounting.

Risks and test signals: high-value signals are edge-case protection against divide-by-zero, negative accounting, and over-capacity effective usage. Exact message assertions make validation precise but may be brittle if exception wording changes without behavioral change.
