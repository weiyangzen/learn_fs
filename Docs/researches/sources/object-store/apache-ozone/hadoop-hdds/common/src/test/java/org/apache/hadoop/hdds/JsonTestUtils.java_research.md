# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/JsonTestUtils.java

## Purpose
`JsonTestUtils` is a final test helper class that centralizes JSON serialization and parsing for Ozone tests. It prevents each test from creating its own Jackson configuration and gives tests a consistent JSON shape.

## APIs and dependencies
The class owns a static `ObjectMapper` and `ObjectWriter`. The mapper excludes null fields, registers `JavaTimeModule`, and disables timestamp-style date serialization. Public helpers include `toJsonStringWithDefaultPrettyPrinter`, `toJsonString`, `valueToJsonNode`, `readTree`, `readTreeAsListOfMaps`, and generic `treeToValue`. It depends on Jackson core/databind annotations, `JsonNode`, `ObjectMapper`, `ObjectWriter`, `TypeReference`, and the Java time datatype module.

## Control flow and state behavior
All state is static and immutable after class initialization. Jackson's mapper is configured before use and then reused, which is safe under the documented ObjectMapper threading model. Methods simply delegate to mapper or writer calls and propagate `IOException` for serialization and parsing failures. There is no filesystem, network, or persistent state.

## Integration points
The helper is intended for test classes that need stable JSON snapshots, JSON tree assertions, or object conversion. The list-of-maps reader is useful for generic API response assertions where test code does not need strong DTO classes.

## Risks and test signals
Because nulls are omitted and date formatting is ISO-like rather than timestamps, tests using this helper encode those expectations. Adding mapper features globally can silently change unrelated tests. The class itself has no direct tests in this subset, so its signal comes from downstream tests that use it.
