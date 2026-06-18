# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerConfiguration.java

Purpose: Configuration bean and validation layer for datanode disk balancer settings.

Important APIs and types: Annotated with `@ConfigGroup`. Defines config keys for info directory, density threshold, bandwidth, parallel threads, default run state, service interval/timeout, container choosing policy, stop-after-even behavior, replica deletion delay, and movable container states. Provides setters with validation, `getMovableContainerStates`, `toProtobufBuilder`, and `updateFromProtobuf`.

Control flow: Numeric setters reject threshold outside `(0,100)`, non-positive bandwidth, and non-positive parallelism. Container-state parsing requires non-empty uppercase enum names, rejects open-to-write, CLOSING, and DELETED states, and returns an unmodifiable set. Proto updates only apply fields present in the proto.

State and persistence: In-memory configuration object; persistence happens when `DiskBalancerInfo` is written to YAML or sent over protobuf.

Dependencies and integration points: Loaded from `ConfigurationSource` by `DiskBalancerService`; mutated through `DiskBalancerProtocolServer` RPCs; converted to/from `HddsProtos.DiskBalancerConfigurationProto`.

Risks: Direct config injection may set raw `containerStates` without setter validation, but reads through `getMovableContainerStates` still validate. `toString` formatting lists fewer key/value rows than the formatted header suggests. Tests should cover invalid state casing, non-movable states, proto partial updates, threshold bounds, and default state set.
