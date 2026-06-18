# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/file/TestOMFileCreateRequestWithFSO.java

FSO specialization of file create tests. It verifies non-recursive parent handling through `directoryTable`, recursive parent creation metrics, overwrite behavior against object-id-qualified FSO key rows, namespace quota, valid `.snapshot` substrings, and open-file lookup under FSO layout.

The class extends `TestOMFileCreateRequest`, overrides `getOMFileCreateRequest` to use `OMFileCreateRequestWithFSO`, returns `BucketLayout.FILE_SYSTEM_OPTIMIZED`, and overrides `verifyPathInOpenKeyTable` to traverse `directoryTable` object IDs before reading `getOpenFileName(volumeId, bucketId, parentId, fileName, clientId)`. `getDirInfo` resolves a directory path through the same parent-chain traversal.

Control flow reuses superclass harnesses while seeding FSO parents with `addParentsToDirTable` and files with `addFileToKeyTable`. Tests fail when parents are absent or a same-name directory exists, then succeed when valid parents exist. Recursive tests create missing parent directories, then verify overwrite true succeeds and overwrite false fails. Snapshot tests allow `.snapshot` only when not used as a reserved root.

State behavior uses FSO open key table names containing volume ID, bucket ID, parent object ID, file name, and client ID. Parent directories are in `directoryTable`; file rows carry parent object IDs. Metrics and bucket namespace count created parent directories. Risks include wrong parent traversal, stale directory rows after key deletes, directory/file confusion, and over-strict snapshot rejection. Signals are inherited create-file assertions, FSO open-key row lookup, quota failure, namespace and metric checks.
