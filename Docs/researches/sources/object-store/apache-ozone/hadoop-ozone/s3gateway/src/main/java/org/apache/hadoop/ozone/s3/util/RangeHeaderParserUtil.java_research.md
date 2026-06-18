<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java

## Purpose
Parses S3 `Range` and copy-source range header values into `RangeHeader`.

## Important APIs, types, and functions
- `parseRangeHeader(String rangeHeaderVal, long length)` matches `S3Consts.RANGE_HEADER_MATCH_PATTERN`.
- Supports explicit `bytes=start-end`, open-ended `bytes=start-`, and suffix `bytes=-count` ranges.
- Marks malformed values as full reads and marks start/end beyond length as invalid when appropriate.

## Control flow
If regex matches, start/end groups are parsed. Missing start means suffix range. Missing end means through `length - 1`. Starts beyond length can become invalid if end is also beyond length, otherwise the parser falls back to full read. Nonmatching headers become full-read responses rather than invalid errors.

## State and persistence behavior
Stateless parser. No persistence.

## Dependencies and integration points
Used by object GET and copy-part source range handling. Depends on `S3Consts.RANGE_HEADER_MATCH_PATTERN`.

## Risks and edge cases
Malformed range units such as `mb=...` become full reads instead of 416. Copy-part callers sometimes pass length `0`, so range semantics differ there. Numeric overflow can throw `NumberFormatException`.

## Test signals
`TestRangeHeaderParserUtil` covers normal ranges, single-byte ranges, invalid starts, unsupported units, suffix ranges, overlong suffixes, and large numeric values. Object GET tests should assert HTTP 206/416 behavior on top of parser output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java -->
