# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerYaml.java

Purpose: verifies persistence and validation of datanode disk balancer YAML info files.

Important APIs/types/functions: `DiskBalancerYaml.createDiskBalancerInfoFile`, `readDiskBalancerInfoFile`, `DiskBalancerInfo`, `DiskBalancerRunningStatus`, `DiskBalancerConfiguration.DEFAULT_CONTAINER_STATES`, and `DiskBalancerVersion.DEFAULT_VERSION`. The `validYaml()` helper provides a baseline persisted document for mutation tests.

Control flow: parameterized round-trip tests write `DiskBalancerInfo` to the default info filename under `@TempDir`, read it back, and compare equality. Missing and explicit-null `containerStates` tests hand-write YAML and assert defaulting. Invalid cases mutate version, operational state, threshold, bandwidth, parallel thread count, or container states and assert `IOException` messages include the expected validation reason.

State and persistence behavior: this is a pure YAML file test. It checks backward-compatible defaults for older/malformed persisted beans and rejects unsupported or invalid persisted configuration before disk balancer resumes from it.

Dependencies and integration points: integrates SnakeYAML-backed disk balancer persistence with config validation and protobuf running-status enums. It uses Java NIO file writes and JUnit parameter sources.

Risks and test signals: strong signal for persisted-info compatibility and safety. Exact substring checks avoid binding to whole exception text but still catch missing validation. Gaps include no explicit malformed YAML syntax case or future-version migration path.
