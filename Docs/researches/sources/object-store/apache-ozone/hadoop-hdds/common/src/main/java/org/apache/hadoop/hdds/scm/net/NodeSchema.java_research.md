# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchema.java

## Purpose
Represents one layer in a network topology schema, including layer type, cost, path prefix, default name, and optional sublayers.

## Important APIs, Types, And Functions
Nested `Builder` validates `type`, defaults cost from type, and builds `NodeSchema`. Fields have standard getters/setters for YAML binding. `matchPrefix` checks case-insensitive prefix match. `LayerType` defines `ROOT`, `INNER_NODE`, and `LEAF_NODE` with descriptions and default costs plus `getType(String)`.

## Control Flow
Schema loaders can instantiate via no-arg constructor then setters, or code can use the builder. Placement/topology creation uses prefix/default name/cost to map network paths.

## State And Persistence
Instances are mutable to support YAML deserialization. Schema configuration is external; this class models it in memory.

## Dependencies And Integration Points
Depends on `NetConstants`. Integrated by network topology schema loading and default schemas.

## Risks And Test Signals
No validation in setters means YAML can produce inconsistent schemas. `getType` returns null for unknown strings. Tests should cover builder validation/defaults, YAML setter path, prefix matching, sublayers, and unknown layer types.
