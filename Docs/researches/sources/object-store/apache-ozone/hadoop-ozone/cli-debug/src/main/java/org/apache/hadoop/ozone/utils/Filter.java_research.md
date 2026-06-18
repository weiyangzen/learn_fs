# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/utils/Filter.java

Purpose: `Filter` is a generic model for representing one comparison operation, value, and optional nested filter map.

Important APIs and types: It exposes constructors accepting `FilterOperator` or string operator names, getters/setters, `getFilterOperator`, `toString`, and enum values `EQUALS`, `LESSER`, `GREATER`, and `REGEX`.

Control flow and state: Instances are mutable. String operator parsing is a simple case-insensitive if/else chain and returns null for unknown operators.

Dependencies and integration points: This utility can represent nested record filters for debug/query tooling, although no direct consumer appears in the listed files.

Risks: Unknown operators silently become null. `value` is `Object`, so consumers need type checks. `nextLevel` defaults to null and is mutable. There is no validation for incompatible operator/value combinations.

Test signals: Tests should cover all operator strings, unknown operator handling, nested filters, mutators, and `toString`.
