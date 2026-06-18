# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/VersionResponse.java

Purpose: higher-level wrapper for SCM software version responses and key/value metadata.

Important APIs and functions: constructors accept version and optional values map. `newBuilder` creates a builder. `getFromProtobuf` converts `SCMVersionResponseProto` key list into a map. `put` and `Builder.addValue` reject duplicate keys. `getProtobufMessage` serializes the version and values to `KeyValue` protobufs. `getValue` reads a value by key. Builder supports `setVersion`, `addValue`, and `build`.

Control flow and state: `values` is mutable in the main object via `put`; builder stores values until build, but passes the map into the constructed response without defensive copy.

Dependencies and integration: used by `StorageContainerNodeProtocol.getVersion` and protocol conversion code for datanode/SCM version negotiation.

Risks and test signals: duplicate handling and map mutability can affect callers. Tests should cover protobuf round trip, duplicate key rejection in both builder and response, missing values, builder mutation after build, and deterministic expectations where value ordering is irrelevant.
