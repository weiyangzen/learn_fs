<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java

## Purpose
Verifies OM permission-denied exceptions are translated into S3 access-denied responses across gateway endpoints.

## Important APIs, types, and functions
Uses mocked `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `ClientProtocol`, `OMException(PERMISSION_DENIED)`, `EndpointBuilder`, `S3ErrorTable.ACCESS_DENIED`, and `EndpointTestUtils` for object/tag operations.

## Control flow
Setup wires mocks and common configuration. Root, bucket, and object endpoint tests inject permission failures into volume lookup, bucket lookup/create/delete/list, multipart listing, key list, ACL get/set, key get/put/delete, multipart initiation, and object tagging get/put/delete. Multi-delete additionally checks per-key `ErrorInfo` is surfaced in the response errors list.

## State and persistence behavior
No real Ozone state is persisted; mocked calls throw or return controlled values. The important state is error propagation: forbidden operations should not be masked as missing resources or internal failures.

## Dependencies and integration points
This spans `RootEndpoint`, `BucketEndpoint`, `ObjectEndpoint`, S3 ACL parsing, multi-delete response construction, and Ozone client protocol methods.

## Risks and edge cases
The mock setup validates translation but not real ACL evaluation. It covers `PERMISSION_DENIED` but not mixed permission and not-found conditions from real OM.

## Test signals
Signals are HTTP 403 or `ACCESS_DENIED` S3 errors for each endpoint path and a multi-delete response error code of `ACCESS_DENIED`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestPermissionCheck.java -->
