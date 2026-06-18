# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFileSystemMetrics.java

Purpose: validates OM `numKeys` metrics for key, file, and directory operations through Ozone filesystem and object-store APIs.

Important APIs/types/functions: enum `TestOps` selects Key, File, or Directory. `testOzoneFileCommit` records `OMMetrics.getNumKeys`, creates either an object-store key, an O3FS file, or a directory, asserts the count increased by two, deletes the parent, and asserts the count returns to the baseline.

Control flow: setup suspends key and directory deleting services, enables filesystem paths, creates a legacy bucket, and opens O3FS. Each test delegates to the common helper with a different operation kind.

State and persistence behavior: operations create a parent plus leaf entry, hence the expected `+2` key count. Recursive delete removes both entries while deletion services are suspended to keep accounting deterministic. OM config is restored and services resumed in cleanup.

Dependencies and integration points: uses `OMMetrics`, `OzoneBucket.createKey`, `FileSystem.create`, `FileSystem.mkdirs`, OM deleting services, and `OmConfig.fileSystemPathEnabled`.

Risks: metric semantics are tightly coupled to how directories are counted in legacy filesystem-path mode. Asynchronous deletion would make assertions flaky if services were not suspended.

Test signals: catches mismatches between OM metadata mutations and exposed `numKeys` metric for object-store keys, filesystem files, and directories.
