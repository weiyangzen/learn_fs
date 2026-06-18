# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerYaml.java

Purpose: Serializes and deserializes `DiskBalancerInfo` to the local `diskBalancer.info` YAML file.

Important APIs and types: `createDiskBalancerInfoFile` writes YAML using SnakeYAML and `YamlUtils.dump`. `readDiskBalancerInfoFile` reads YAML into nested `DiskBalancerInfoYaml`, validates required fields/version/container states, creates `DiskBalancerInfo`, and validates it via `toConfiguration`.

Control flow: On read, missing `operationalState` or version throws `IOException`; unsupported version throws `IOException`; missing/blank container states defaults to `CLOSED,QUASI_CLOSED`; malformed YAML is wrapped as `IOException`. On write, only persisted fields are included: operational state, threshold, bandwidth, parallel thread, stop-after-even, container states, and version.

State and persistence: This is the persistence boundary for disk balancer service config and running status. Report-only fields such as ideal usage and volume reports are intentionally omitted.

Dependencies and integration points: Called by `DiskBalancerService` during load, refresh, stop-after-even, and node-state persistence. Uses `DiskBalancerVersion` and `DiskBalancerConfiguration` for validation.

Risks: Flow-style YAML may be less readable but compact. Backward compatibility for absent `containerStates` is handled by defaulting, but missing version is not tolerated. Tests should cover malformed YAML, missing fields, unsupported versions, invalid persisted config values, default container states, and write/read round trip.
