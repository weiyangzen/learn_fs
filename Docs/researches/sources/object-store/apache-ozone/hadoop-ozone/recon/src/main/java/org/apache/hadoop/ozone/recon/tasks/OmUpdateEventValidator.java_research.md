# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmUpdateEventValidator.java

Purpose: `OmUpdateEventValidator` validates that an OM DB update event value type matches the expected value type declared by `OMDBDefinition` for the event table.

Important APIs and types: the constructor takes an `OMDBDefinition`. `isValidEvent(String tableName, Object actualValueType, Object keyType, OMDBUpdateAction action)` compares `omdbDefinition.getColumnFamily(tableName).getValueType().getName()` with `actualValueType.getClass().getName()`. `setLogger` is test-only support for verifying warnings.

Control flow and integration: callers use the validator before handing decoded events to task processing. On mismatch it logs table, key, action, expected type, and actual type, then returns false.

State and persistence: state is just the OM DB definition reference and a static logger. It has no durable writes and no metrics.

Dependencies: `OMDBDefinition`, `OMDBUpdateEvent.OMDBUpdateAction`, SLF4J.

Risks and test signals: `actualValueType` and `keyType` are dereferenced without null checks, so null event values can throw if not filtered by callers. `getColumnFamily(tableName)` must exist. Tests should cover matching types, mismatches with logged details, invalid table names, and null handling expectations.
