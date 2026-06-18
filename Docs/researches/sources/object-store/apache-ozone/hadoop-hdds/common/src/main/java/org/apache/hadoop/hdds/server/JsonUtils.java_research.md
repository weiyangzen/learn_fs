# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/server/JsonUtils.java

## Purpose
Shared Jackson JSON utility for HDDS/Ozone server code, including pretty printing, streaming sequence IO, tree creation, file read/write, and checksum serialization.

## Important APIs and types
`toJsonStringWithDefaultPrettyPrinter`, `toJsonString`, and `toJsonStringWIthIndent` serialize objects. `getSequenceWriter` writes JSON arrays to an output stream and closes it; `getStdoutSequenceWriter` avoids closing `System.out`. `createArrayNode`, `createObjectNode`, `readTree`, `readFromReader`, `getDefaultMapper`, `writeToFile`, and `readFromFile` expose Jackson operations. `ChecksumSerializer` serializes long checksums through `HddsUtils.checksumToString`.

## Control flow and state
Static mappers are initialized once, omit nulls, register `JavaTimeModule`, and write Java time values as ISO strings rather than timestamps. `toJsonStringWIthIndent` catches `JsonProcessingException`, logs, and returns `{}`. `NonClosingOutputStream` delegates writes/flushes but ignores close.

## Dependencies and integration points
Depends on Jackson core/databind/JSR310, `HddsUtils`, and SLF4J. CLI, admin, web, and persistence helpers can use it for consistent JSON formatting.

## Risks and test signals
Tests should cover Java time serialization, null omission, sequence writer close behavior, stdout non-close behavior, file streaming round trips, checksum string formatting, and the typo-preserved method name `toJsonStringWIthIndent`. Returning `{}` on serialization errors can mask failures.
