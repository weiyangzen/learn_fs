# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestO3FSWithFSO.java

Purpose: concrete O3FS selector for the file-system-optimized bucket-layout test suite.

Important APIs/types/functions: extends `AbstractOzoneFileSystemTestWithFSO` and invokes its default constructor under `@TestInstance(PER_CLASS)`.

Control flow: local class only binds inherited tests to the FSO O3FS configuration.

State and persistence behavior: inherits FSO-specific path, key-table, and directory semantics from the parent fixture.

Dependencies and integration points: depends on `AbstractOzoneFileSystemTestWithFSO`, which supplies cluster setup and actual test methods.

Risks: coverage relies entirely on the superclass. A constructor or superclass change changes all behavior here.

Test signals: inherited failures signal O3FS FSO regressions in the shared filesystem contract.
