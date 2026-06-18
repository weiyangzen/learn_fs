# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCreateTest.java

Purpose: `AbstractContractCreateTest` is the main create/write contract suite. It validates normal create, overwrite behavior, directory conflicts, visibility timing, file status block sizes, implicit parent creation, creation under files, mkdir under files, and `Syncable` stream capabilities.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem.create`, `FSDataOutputStream`, `FSDataInputStream`, `FileStatus`, `StreamCapabilities`, `ContractTestUtils.writeDataset`, `writeTextFile`, `touch`, `getFileStatusEventually`, `assertCapabilities`, and IO statistics logging. It has a custom `path(String, boolean)` naming helper to distinguish builder and non-builder cases, `CREATE_TIMEOUT`, `validateBlockSize`, `expectCreateUnderFileFails`, `expectMkdirsUnderFileFails`, and `validateSyncableSemantics`.

Control flow: paired helper tests run against both builder and classic create paths. They create new files, reject no-overwrite over existing files, accept overwrite with changed data, and reject overwriting empty/non-empty directories unless contract flags permit a skip. Visibility tests probe existence before write, after flush, and after close using `CREATE_VISIBILITY_DELAYED` and `IS_BLOBSTORE` flags to downgrade object-store timing differences. Path hierarchy tests assert parent directories are populated and file-as-directory paths fail. `testSyncable` derives hflush/hsync expectations from contract flags and verifies stream capability declarations plus visible reads after hsync when supported.

State and persistence behavior: the class creates and overwrites persistent file contents, validates namespace materialization, checks metadata length/block size, and reads back flushed or synced data. It explicitly models eventual visibility with `getFileStatusEventually`.

Dependencies and integration points: tightly coupled to `ContractOptions` feature flags, `ContractTestUtils`, Hadoop stream capabilities, and the concrete filesystem's builder API implementation.

Risks and test signals: catches stale overwrite reads, accidental directory replacement, file-under-file namespace bugs, incomplete parent directory creation, incorrect strict/relaxed exception policy, wrong block-size metadata, and misleading hflush/hsync capability reporting. Durability itself is not provable; the test uses new-reader visibility as the practical signal.
