# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/net/NodeSchemaLoader.java

## Purpose
`NodeSchemaLoader` is the parsing and validation utility for SCM network topology schema files. It accepts either XML or YAML input, normalizes the result into an ordered root-to-leaf `List<NodeSchema>`, and returns that list with the topology `enforcePrefix` flag in `NodeSchemaLoadResult`.

## Important APIs, Types, And Functions
`getInstance()` exposes a process-wide singleton. `loadSchemaFromFile()` resolves an absolute/relative filesystem path first, then falls back to the context class loader. `loadSchemaFromStream()` dispatches by filename extension. XML parsing flows through `loadSchema()`, `loadLayoutVersion()`, `loadLayersSection()`, `loadTopologySection()`, and `parseLayerElement()`. YAML parsing uses `YamlUtils.loadAs(..., NodeSchema.class)` and follows the first sublayer chain.

## Control Flow
XML files must have one `<configuration>`, one `<layoutversion>` equal to `1`, one `<layers>`, and one `<topology>`. Layer definitions are parsed into a map keyed by layer id, then topology `<path>` orders those ids and verifies the path starts with `ROOT`, ends with `LEAF_NODE`, and has the same depth as the layer set. YAML files are expected to deserialize into a root `NodeSchema` and then a linear first-child path.

## State, Persistence, And Dependencies
The loader is stateless except for a non-synchronized volatile singleton. It reads schema files/resources only and persists nothing. It depends on secure XML parsing via `XMLUtils.newSecureDocumentBuilderFactory()`, Apache Commons helpers, `YamlUtils`, `NodeSchema`, `NetConstants`, and DOM APIs.

## Integration Points
`NodeSchemaManager` uses this class during SCM network topology initialization. The resulting schema list drives path completion, network levels, and topology costs used by placement and sorting code.

## Risks
The singleton initialization is not fully synchronized, though duplicate instances are harmless because the class holds no mutable parse state. YAML parsing only follows `getSublayer().get(0)`, so branching schemas are ignored. XML duplicate detection uses `schemas.containsValue(schema)`, so it depends on `NodeSchema.equals()` semantics. A bad YAML extension such as `.yml` falls through to XML parsing because only `.yaml` is recognized.

## Test Signals
Useful tests cover missing files, classpath resource loading, invalid layout versions, duplicate root/leaf layers, prefix enforcement failures, bad topology paths, YAML root/leaf validation, and `.yaml` versus XML dispatch.
