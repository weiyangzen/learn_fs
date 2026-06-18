# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerInfo.java

Purpose: Mutable data transfer and persistence model for disk balancer status and configuration. It separates persisted configuration/state from report-only live fields.

Important APIs and types: Holds `DiskBalancerRunningStatus`, threshold, bandwidth, parallel thread count, stop-after-even, version, success/failure counts, bytes-to-move, balanced bytes, density, container states, ideal usage, and per-volume report protos. Provides constructors, `updateFromConf`, `toConfiguration`, getters/setters, `equals`, and `hashCode`.

Control flow: The boolean constructor maps `shouldRun` to RUNNING or STOPPED and copies config values. `toConfiguration` reconstructs a validated `DiskBalancerConfiguration`, which is used before persistence/application.

State and persistence: This is the object persisted to `diskBalancer.info` through `DiskBalancerYaml`, but comments indicate `idealUsage` and `volumeInfo` are report-only and not persisted.

Dependencies and integration points: Produced by `DiskBalancerService.getDiskBalancerInfo`, consumed by `DiskBalancerProtocolServer`, and serialized by `DiskBalancerYaml`.

Risks: `equals` excludes counters, bytes, density, ideal usage, and volume info, intentionally treating those as operational/report state rather than configuration identity. Setters do not validate directly; validation occurs through conversion to `DiskBalancerConfiguration`. Tests should cover persisted-vs-report fields, config round trips, version/default constructor behavior, and equality semantics.
