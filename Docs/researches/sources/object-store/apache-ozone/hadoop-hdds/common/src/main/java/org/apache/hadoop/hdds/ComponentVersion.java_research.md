## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ComponentVersion.java

**Purpose:** Defines a common interface for HDDS component version enums, tying human-readable descriptions and protobuf wire values to the generic Ozone `Versioned` contract.

**Important APIs/types/functions:** `description()` returns a textual description for an enum value. `toProtoValue()` returns the integer value used in protocol messages. The default `version()` implementation delegates to `toProtoValue()`, satisfying `Versioned`.

**Control flow:** No branching beyond default method dispatch. Implementing enums supply concrete values.

**State and persistence:** Interface has no state. Implementing enum constants represent persisted/wire compatibility states because `toProtoValue()` is serialized in protocols.

**Dependencies and integration points:** Depends on `org.apache.hadoop.ozone.Versioned`. Implemented by `DatanodeVersion` in this subset and likely other component version enums. Used anywhere feature gates compare component versions.

**Risks:** Wire values must remain stable; changing `toProtoValue()` behavior in implementers can break compatibility. The interface assumes integer versions are sufficient for ordering and serialization.

**Test signals:** Indirectly covered by component version enum tests and protocol compatibility tests. No direct unit test in this subset.
