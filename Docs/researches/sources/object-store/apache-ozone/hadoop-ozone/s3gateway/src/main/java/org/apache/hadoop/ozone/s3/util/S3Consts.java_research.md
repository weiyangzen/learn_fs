<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java

## Purpose
Central constants for S3 gateway headers, query parameters, XML namespace, tagging limits, range parsing, copy directives, payload-signing markers, and S3 Express defaults.

## Important APIs, types, and functions
- Header constants include copy source/range, storage class, content SHA-256, custom metadata, tagging, bucket-owner conditions, checksum, and conditional request headers.
- Payload constants cover unsigned and streaming AWS4 payload marker values.
- Range constants include `RANGE_HEADER_MATCH_PATTERN` and 416 status value.
- Tag limits and regex define S3 tag validation policy.
- `CopyDirective` enum models `COPY` and `REPLACE`.
- `QueryParams` nests all S3 gateway query parameter names.

## Control flow
No executable logic beyond enum/static initialization. Consumers import constants to keep endpoints and utilities aligned.

## State and persistence behavior
Static immutable constants only. No persistence.

## Dependencies and integration points
Used throughout endpoint, signature, util, and exception code. Constants must align with AWS S3 wire names and Ozone endpoint query routing.

## Risks and edge cases
Changing a constant changes public API compatibility. Header casing matters where JAX-RS lookups are case-insensitive in practice but code may compare literal strings. Tag regex and limits define the accepted client surface.

## Test signals
Tests should indirectly pin constants through API behavior: copy directives, conditional headers, tagging validation, range parsing, S3 Express listing, and signature payload modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java -->
