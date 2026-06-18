<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java

## Purpose
Provides a stricter RFC 1123-style date formatter for S3 response headers, especially `Last-Modified`.

## Important APIs, types, and functions
- Static `FORMAT` is a `DateTimeFormatter`.
- Formatter uses English day/month abbreviations, two-digit day of month, four-digit year, optional seconds parsing, and Ozone time zone offset.

## Control flow
The formatter is built once in a static block using `DateTimeFormatterBuilder`.

## State and persistence behavior
Static immutable formatter only. No persistence.

## Dependencies and integration points
Used by `ObjectEndpoint.addLastModifiedDate` and tested by `TestRFC1123Util`. Depends on `OzoneConsts.OZONE_TIME_ZONE`.

## Risks and edge cases
The formatter emits numeric offset based on Ozone timezone rather than a literal `GMT` token. The two-digit day is intentional for Go client compatibility.

## Test signals
Tests should verify single-digit days are formatted with leading zero, month/day abbreviations, timezone suffix, and compatibility with S3 clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java -->
