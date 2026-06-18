<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java

## Purpose
Focused tests for common `EndpointBase` metadata parsing used by S3 endpoint implementations.

## Important APIs, types, and functions
The file exercises `EndpointBase.getCustomMetadataFromHeaders(MultivaluedMap)`, `S3Consts.CUSTOM_METADATA_HEADER_PREFIX`, `OzoneConsts.GDPR_FLAG`, and `OS3Exception` error reporting.

## Control flow
Tests build synthetic request header maps, instantiate an anonymous `EndpointBase`, and call the metadata extraction helper. Assertions verify accepted custom metadata, rejected reserved GDPR metadata, maximum metadata-size enforcement, and case-insensitive matching of the `x-amz-meta-` prefix.

## State and persistence behavior
No Ozone state is created. The method returns a new metadata map derived from request headers; server-controlled metadata such as GDPR must be excluded so callers cannot persist it through user headers.

## Dependencies and integration points
This helper feeds object creation, copy, and multipart initiation paths that persist metadata into Ozone key metadata. It also maps S3 metadata size rules to `MetadataTooLarge`.

## Risks and edge cases
The size test uses one oversized value and does not cover many small headers whose aggregate size crosses the limit. Header casing is covered for the prefix, but duplicate values and non-ASCII byte accounting are not deeply exercised.

## Test signals
Signals are exact map membership and an `OS3Exception` whose code contains `MetadataTooLarge`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestEndpointBase.java -->
