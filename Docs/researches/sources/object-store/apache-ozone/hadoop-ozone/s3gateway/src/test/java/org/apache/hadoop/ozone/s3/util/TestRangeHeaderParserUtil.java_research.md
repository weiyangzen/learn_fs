<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java

## Purpose
Tests S3/HTTP byte range header parsing.

## Important APIs, types, and functions
Uses `RangeHeaderParserUtil.parseRangeHeader`, `RangeHeader.getStartOffset`, `getEndOffset`, `isReadFull`, and `isInValidRange`.

## Control flow
One test method checks normal ranges, same start/end, invalid range beyond file length, reversed ranges that fall back to full read, wrong range units, malformed negative ranges, suffix ranges, suffix longer than file length, and large long-valued ranges.

## State and persistence behavior
No persistence. Parser returns a value object describing either a bounded range, full-read fallback, or invalid range.

## Dependencies and integration points
Object GET uses this parser to set read offsets, `Content-Range`, and partial-content status.

## Risks and edge cases
Multi-range headers, whitespace variants, open-ended large ranges, and zero-length objects are not covered.

## Test signals
Signals are exact start/end offsets, full-read flags, invalid-range flags, and support for offsets above 32-bit integer range.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/util/TestRangeHeaderParserUtil.java -->
