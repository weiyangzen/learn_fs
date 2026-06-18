# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOFSWithFSO.java

Purpose: concrete rooted OFS selector for the file-system-optimized bucket-layout test suite.

Important APIs/types/functions: extends `AbstractRootedOzoneFileSystemTestWithFSO` and passes `false` to its constructor.

Control flow: no local tests; inherited rooted FSO tests execute under PER_CLASS lifecycle.

State and persistence behavior: exercises FSO metadata and rooted path behavior supplied by the superclass.

Dependencies and integration points: depends on `AbstractRootedOzoneFileSystemTestWithFSO`.

Risks: local coverage is wholly delegated; the meaning of the boolean constructor flag must remain consistent with the superclass.

Test signals: failures come from inherited OFS FSO filesystem behavior tests.
