# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/resources/network-topology-default.yaml

## Purpose
This YAML resource defines the default network topology schema in the newer tree-shaped YAML format. It represents root, rack, and leaf node layers for HDDS/Ozone topology parsing.

## Important APIs, Types, And Functions
The document root describes the root layer with `cost: 1`, `prefix: /`, `type: ROOT`, and `defaultName: datacenter`. Its `sublayer` list contains a rack `INNER_NODE` with `cost: 1`, `prefix: rack`, and `defaultName: rack`. The rack sublayer contains a leaf node with `defaultName: node`, `type: LEAF_NODE`, and `prefix: node`.

## Control Flow
YAML schema loading reads the root layer first, then recursively walks `sublayer` lists to build a topology tree. Unlike the XML comments, the YAML comments state that `prefix` must be explicitly specified for inner nodes. The resulting schema is used to validate and normalize node locations.

## State And Persistence
The file is static classpath configuration. Parsed layer definitions become in-memory schema state used by network topology code; no runtime writes occur.

## Dependencies And Integration Points
Depends on the repository's YAML schema loader and SnakeYAML path. `TestYamlSchemaLoader` references `network-topology-default.yaml` directly, making it the primary test fixture for YAML topology parsing.

## Risks
The YAML default differs from XML defaults: root has prefix `/`, rack default name is `rack` rather than `/default-rack`, and leaf prefix is `node` rather than empty. Code that assumes XML/YAML equivalence may produce different validation behavior. Because `sublayer` is a list even when only one child exists, parser code must handle list traversal consistently.

## Test Signals
Schema loader tests should assert root/rack/node types, costs, prefixes, default names, recursive sublayer parsing, and invalid YAML handling. Integration tests should compare expected rack/node placement behavior when the YAML schema is selected.
