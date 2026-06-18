## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/DatanodeVersion.java

**Purpose:** Enumerates datanode protocol/feature versions and exposes the current datanode version for compatibility checks.

**Important APIs/types/functions:** Enum constants are `DEFAULT_VERSION(0)`, `SEPARATE_RATIS_PORTS_AVAILABLE(1)`, `COMBINED_PUTBLOCK_WRITECHUNK_RPC(2)`, `STREAM_BLOCK_SUPPORT(3)`, and `FUTURE_VERSION(-1)`. `CURRENT` is computed by `latest()` and `CURRENT_VERSION` exposes its integer. `BY_PROTO_VALUE` maps serialized integers to enum constants. `description()` and `toProtoValue()` implement `ComponentVersion`. `fromProtoValue(int)` returns the matching enum or `FUTURE_VERSION` for unknown newer values. `latest()` returns the second-to-last enum constant, intentionally excluding `FUTURE_VERSION`.

**Control flow:** Static initialization builds the lookup map and selects current version. Runtime conversion branches through `Map.getOrDefault`. Adding new versions before `FUTURE_VERSION` automatically advances `CURRENT`.

**State and persistence:** Enum constants and static lookup map are immutable runtime state. Integer proto values are persistent wire/state compatibility markers and must not be reused.

**Dependencies and integration points:** Implements `ComponentVersion` and therefore `Versioned`. Integrated by datanode/client compatibility logic, including stream block support gates tied to `STREAM_BLOCK_SUPPORT`.

**Risks:** New real versions must be inserted before `FUTURE_VERSION`; appending after it would break `latest()`. Duplicate proto values would fail during static map collection or create compatibility ambiguity. Unknown values intentionally collapse to `FUTURE_VERSION`, so callers must handle newer servers conservatively.

**Test signals:** No direct test in this subset. Stream-read tests indirectly depend on the feature represented by `STREAM_BLOCK_SUPPORT`, but not on this enum mapping.
