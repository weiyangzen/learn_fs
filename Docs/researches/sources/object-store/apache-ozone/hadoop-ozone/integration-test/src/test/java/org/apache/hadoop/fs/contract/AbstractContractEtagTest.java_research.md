# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractEtagTest.java

Purpose: `AbstractContractEtagTest` verifies filesystem etag support for filesystems that advertise etags. It checks availability, non-empty etag values, consistency across metadata retrieval APIs, content sensitivity, rename preservation when declared, and located-status/list-files propagation.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `CommonPathCapabilities.ETAGS_AVAILABLE`, `ETAGS_PRESERVED_IN_RENAME`, `EtagSource`, `FileStatus`, `LocatedFileStatus`, `FileSystem`, `Path`, Ratis `Preconditions.assertInstanceOf`, AssertJ assertions/assumptions, and `ContractTestUtils.createFile`/`touch`. Helper `etagFromStatus(FileStatus)` asserts the status implements `EtagSource` and returns a non-blank etag.

Control flow: `testEtagConsistencyAcrossListAndHead` asserts the path capability, touches a file, reads its `getFileStatus` etag, then checks `listStatus(path)` returns a single status with the same etag. `testEtagsOfDifferentDataDifferent` overwrites a file with same-length different data and requires a changed etag. `testEtagConsistencyAcrossRename` assumes rename preservation capability, creates source data, captures the etag, renames, and verifies destination etag equality. `testLocatedStatusAlsoHasEtag` compares `getFileStatus`, `listLocatedStatus`, and `listFiles`.

State and persistence behavior: persisted object data and metadata changes drive etag values. The overwrite test prevents implementations from using only path or length. Rename behavior is conditional on a declared capability.

Dependencies and integration points: relies on Hadoop `FileStatus` implementations also implementing `EtagSource`. Integrates list planning/query use cases by ensuring list APIs expose usable etags.

Risks and test signals: catches blank etags, missing `EtagSource`, inconsistent HEAD vs LIST metadata, etags insensitive to data changes, unsupported rename preservation claims, and missing etags in located listings. It does not define etag format or cryptographic strength.
