<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java

## Purpose
Simple value object holding parsed S3 byte range offsets and flags for full-read or invalid-range handling.

## Important APIs, types, and functions
- Fields are `startOffset`, `endOffset`, `readFull`, and `inValidRange`.
- Getters expose the parsed values.
- `toString` aids debug logging.

## Control flow
Constructed by `RangeHeaderParserUtil`; consumed by object GET and copy-part range handling.

## State and persistence behavior
In-memory parsed request state only. No persistence.

## Dependencies and integration points
Used by `ObjectEndpoint` and `RangeHeaderParserUtil`.

## Risks and edge cases
The flag name `inValidRange` means invalid range, but the spelling can be read as "in valid range". Consumers must check `isInValidRange` carefully.

## Test signals
Range parser tests should assert exact start/end/full/invalid values for normal, suffix, over-long, and malformed ranges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java -->
