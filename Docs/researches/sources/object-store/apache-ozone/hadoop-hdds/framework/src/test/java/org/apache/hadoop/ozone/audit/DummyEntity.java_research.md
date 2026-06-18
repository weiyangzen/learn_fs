# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/audit/DummyEntity.java

Purpose: Simple test implementation of `Auditable` that exposes two mutable key/value fields as audit parameters.

Important APIs/types/functions: `DummyEntity`, getters/setters for `key1` and `key2`, and `toAuditMap`.

Control flow: Constructor initializes default values. `toAuditMap` creates a new `HashMap` containing the two current field values.

State and persistence behavior: In-memory mutable fields only; no persistence.

Dependencies and integration points: Used by audit logger tests to provide message parameters through the production `Auditable` contract.

Risks: HashMap iteration order is not guaranteed, though audit tests generally check value presence rather than relying entirely on map order.

Test signals: Provides stable audit parameter data for formatted message assertions.
