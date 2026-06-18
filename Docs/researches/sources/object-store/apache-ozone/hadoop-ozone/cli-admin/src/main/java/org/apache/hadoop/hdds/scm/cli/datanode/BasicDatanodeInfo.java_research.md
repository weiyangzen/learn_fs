# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/BasicDatanodeInfo.java

## Purpose
Defines a JSON-friendly DTO for datanode list output, optionally enriched with usage and volume-health fields.

## Important APIs, Types, And Functions
`BasicDatanodeInfo` wraps `DatanodeDetails`, health/op states, optional usage fields, volume counts, and failed volumes. The nested `Builder` builds from `HddsProtos.Node` and optional `withUsageInfo`. Getters are ordered with `@JsonProperty` and omit nullable or empty fields with Jackson annotations.

## Control Flow
Construction converts protobuf datanode details to `DatanodeDetails`, extracts first health and operational states, optional volume counters, and failed volume paths.

## State And Persistence
Immutable DTO after construction; no persistence.

## Dependencies And Integration Points
Used by `ListInfoSubcommand` for JSON and text rendering. Depends on Jackson annotations, `DatanodeDetails`, and `HddsProtos.Node`.

## Risks And Test Signals
The builder assumes `node.getNodeStates(0)` and `getNodeOperationalStates(0)` exist. Tests should cover nodes with optional volume fields, failed volumes, usage enrichment, JSON ordering/null omission, and malformed protobuf edge cases.
