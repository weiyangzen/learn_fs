# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/key/TestOMKeyRenameResponseWithFSO.java

Purpose: FSO specialization of single-key rename response tests.

Important APIs/types/functions: Uses `OMKeyRenameResponseWithFSO`, `getOzonePathKey`, `addFileToKeyTable`, synthetic `fromKeyParent`/`toKeyParent`, `bucketInfo`, and `TestOMResponseUtils.createBucket`.

Control flow: Overrides key-info creation to assign object and parent IDs. The source key is added to the FSO key table. Response construction creates parent key infos and bucket info, then passes old/new FSO DB keys and parent metadata into `OMKeyRenameResponseWithFSO`. Inherited tests assert source-to-target move and parent/bucket writes.

State/persistence: Success moves the file-table entry, writes parent directories to `directoryTable`, and writes bucket info. Error response should leave source key and not create parent rows.

Dependencies/integration: Depends on FSO DB key construction with volume/bucket IDs and parent object ID. Uses inherited key response fixture for metadata setup.

Risks/test signals: `createParent` uses random volume/bucket names for the bucket info distinct from the base fixture, so bucket-table assertions validate the response's supplied bucket info, not necessarily the renamed key's bucket. Parent metadata is synthetic.
