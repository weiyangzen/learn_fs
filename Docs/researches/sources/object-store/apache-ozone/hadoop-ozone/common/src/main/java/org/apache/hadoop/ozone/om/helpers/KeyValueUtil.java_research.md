# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyValueUtil.java

Purpose: Utility for converting string maps to and from HDDS `KeyValue` protobuf lists.

Important APIs/types/functions: `getFromProtobuf(List<KeyValue>)` collects protobuf keys and values into a map. `toProtobuf(Map<String,String>)` emits a list of `KeyValue` protos in the map's iteration order.

Control flow and state: Stateless static utility. Duplicate keys during `getFromProtobuf` use `Collectors.toMap` default duplicate handling, which throws.

State and persistence behavior: Used heavily in persisted metadata/tag protobuf fields for keys, buckets, and directories.

Dependencies and integration points: Integrates with `HddsProtos.KeyValue` and helper classes extending `WithMetadata`.

Risks: Duplicate protobuf keys are fatal. Null keys or values will fail during protobuf build or map collection. Output list ordering depends on input map implementation.

Test signals: Round trip maps, duplicate-key rejection, empty maps/lists, and deterministic ordering when using `LinkedHashMap` or immutable maps.
