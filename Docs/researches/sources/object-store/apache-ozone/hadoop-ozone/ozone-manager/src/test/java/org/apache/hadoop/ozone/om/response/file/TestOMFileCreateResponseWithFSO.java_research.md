# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/file/TestOMFileCreateResponseWithFSO.java

Purpose: Specializes the generic key-create response test to cover `OMFileCreateResponseWithFSO`.

Important APIs/types/functions: Extends `TestOMKeyCreateResponse`; overrides `getOmKeyInfo`, `getOpenKeyName`, `getOmKeyCreateResponse`, and `getBucketLayout`. Uses `OMFileCreateResponseWithFSO`, `getOpenFileName`, volume/bucket IDs, bucket object ID as parent, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: Inherited tests create success and error OM responses. This subclass supplies FSO-specific key info with object ID, parent object ID, and update ID, computes the open-file table key, and returns the FSO response object.

State/persistence: Inherited success path writes to the FSO open key table; inherited error path remains a no-op. Parentage is represented by numeric object IDs rather than slash-separated key strings.

Dependencies/integration: Couples file-response FSO behavior to the key-create base test and `OMRequestTestUtils`.

Risks/test signals: The test reuses key-create assertions, so it mainly validates table keying and response class selection. It does not create parent directories beyond using the bucket object ID.
