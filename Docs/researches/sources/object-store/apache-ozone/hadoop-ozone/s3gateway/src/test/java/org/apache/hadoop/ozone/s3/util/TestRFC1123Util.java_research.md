<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java

## Purpose
Tests RFC1123 date parser/formatter leniency for one-digit day values.

## Important APIs, types, and functions
Uses `RFC1123Util.FORMAT.parse` and `RFC1123Util.FORMAT.format` over a `TemporalAccessor`.

## Control flow
The test parses `Mon, 5 Nov 2018 15:04:05 GMT`, formats it back, and asserts the normalized two-digit day form `Mon, 05 Nov 2018 15:04:05 GMT`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
RFC1123 parsing is used by S3 conditional headers such as `If-Modified-Since`, `If-Unmodified-Since`, and copy-source timestamp conditions.

## Risks and edge cases
Only one one-digit-day example is covered. Other HTTP date variants, invalid zones, leap seconds, and locale issues are not tested here.

## Test signals
Passing means the formatter accepts a one-digit day and emits normalized RFC1123 output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRFC1123Util.java -->
