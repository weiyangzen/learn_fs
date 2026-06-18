# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerConfiguration.java

## Purpose
Typed configuration model for Container Balancer. It validates and serializes thresholds, iteration limits, datanode/container include-exclude filters, movement byte limits, timeouts, network-topology behavior, DU refresh trigger, and non-standard container inclusion.

## Important APIs, Types, And Functions
Annotated `@Config` fields bind balancer keys. APIs include threshold percentage/ratio getters, setters with validation for threshold, iteration count, and datanode percentage, include/exclude container parsers, include/exclude node parsers, duration getters/setters, `toString`, `toProtobufBuilder`, and static `fromProtobuf`.

## Control Flow
The configuration framework populates defaults from `OzoneConfiguration`. Runtime/admin input can update fields through setters. Protobuf conversion exports active config and applies provided fields over a fresh configuration object.

## State And Persistence
The object holds mutable in-memory config. Persistent sources are Ozone config files and optional protobuf command/API payloads. Include/exclude containers are stored as comma-separated strings and parsed on access.

## Dependencies And Integration Points
Depends on HDDS config annotations, `OzoneConfiguration`, `ContainerID`, `OzoneConsts`, and `ContainerBalancerConfigurationProto`. Integrated by SCM ContainerBalancer scheduling and admin APIs.

## Risks And Test Signals
Container list parsing can throw on blanks or invalid IDs. Size limits lack setter validation. `fromProtobuf` is package-private, limiting external use. Tests should cover validation boundaries, string parsing, protobuf round trip, duration units, and `toString` output for defaults/non-defaults.
