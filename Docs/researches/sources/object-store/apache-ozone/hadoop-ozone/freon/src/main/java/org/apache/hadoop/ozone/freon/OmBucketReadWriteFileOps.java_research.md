## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/OmBucketReadWriteFileOps.java

Purpose: Freon subcommand `obrwf` that measures mixed file create/list behavior through Hadoop FS paths.

Important APIs/types/functions: extends `AbstractOmBucketReadWriteOps`. Options configure root path, number of files for read prepopulation, and number of files for write batches. Implements `display`, `initialize`, `mainMethod`, `createPath`, `getReadCount`, and `create`.

Control flow: base `call` prints shared config and invokes `initialize`. This command obtains a FileSystem for `rootPath`, then `runTests(mainMethod)`. Each main task runs inherited `readOperations` and `writeOperations`, prints total files read/written, and leaves TODO hooks for read/write lock metrics.

State and persistence behavior: creates directories/files under `rootPath/readPath` and `rootPath/writePath`. Local state holds a shared `FileSystem`.

Dependencies and integration points: Hadoop FS, `AbstractOmBucketReadWriteOps`, Ozone path constants.

Risks: shared FileSystem is used by nested read/write thread pools; no explicit close of `fileSystem`; `createPath` calls `mkdirs` during each list, which adds metadata writes to read workload.

Test signals: count files returned by `listStatus` and created files under write path; metrics timer is inherited.
