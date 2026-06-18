# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OmMetricsInfo.java

Purpose: `OmMetricsInfo` is a Jackson-serializable bean used to persist OM metrics seed data across restart. At present it stores only `numKeys`.

Important APIs and types: package-private default constructor initializes `numKeys` to zero. `getNumKeys()` and `setNumKeys(long)` expose the field. `@JsonProperty` on the private field supports JSON serialization/deserialization.

Control flow: no branching beyond construction.

State and persistence: the `numKeys` value is intended for a file persisted outside the OM RocksDB metadata path so OM metrics can be initialized on restart.

Dependencies and integration points: depends on Jackson annotations and is likely used by OM metrics save/load code. It intentionally stays simple to preserve file compatibility.

Risks: expanding this object changes the persisted metrics file contract. The constructor is package-private, so external serializers/tests must be in-package or use Jackson field access. No validation prevents negative values.

Test signals: serialization round-trip tests should verify default zero, non-zero values, compatibility with missing fields, and rejection or handling policy for invalid negative input if introduced.
