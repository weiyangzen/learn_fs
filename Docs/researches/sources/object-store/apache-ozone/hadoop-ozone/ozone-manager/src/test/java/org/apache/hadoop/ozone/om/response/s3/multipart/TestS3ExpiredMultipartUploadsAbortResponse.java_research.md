# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/s3/multipart/TestS3ExpiredMultipartUploadsAbortResponse.java

Purpose: Parameterized tests for aborting expired multipart uploads across default and FSO bucket layouts.

Important APIs/types/functions: Uses `S3ExpiredMultipartUploadsAbortResponse`, `OmMultipartAbortInfo`, `OmMultipartKeyInfo`, `OMMultipartUploadUtils`, `OMRequestTestUtils.addMultipartKeyToOpenKeyTable/addMultipartKeyToOpenFileTable`, `multipartInfoTable`, open key table, and `deletedTable`.

Control flow: Helpers create random MPUs in random buckets, optionally with part metadata. Success tests pass only one MPU map to the response, commit, and verify those MPUs are removed while a second set remains. Non-empty part test additionally verifies every part is moved to `deletedTable`. Error test uses INTERNAL_ERROR and verifies multipart info and delete tables are unchanged.

State/persistence: Mutates `multipartInfoTable`, layout-specific open key table, and `deletedTable` for part cleanup. Keeps MPUs grouped by `OmBucketInfo` in the response payload.

Dependencies/integration: Integrates MPU utility key construction, layout-specific open MPU records, part protobuf conversion to `OmKeyInfo`, and bucket object IDs for repeated delete entries.

Risks/test signals: The same `createPartKeyInfo` helper is used for both layouts, so FSO-specific part-name shape is less strict here than in dedicated FSO MPU tests. Typos in comments do not affect behavior. Core signal is selective abort and part cleanup only for OK status.
