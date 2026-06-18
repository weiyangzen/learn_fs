# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractContentSummaryTest.java

Purpose: `AbstractContractContentSummaryTest` checks `FileSystem.getContentSummary(Path)` for a directory tree and for a missing path. It is a narrow contract suite around directory and file count reporting.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem`, `ContentSummary`, `Path`, `ContractTestUtils.touch`, AssertJ assertions, and JUnit `assertThrows`. It expects standard `FileNotFoundException` behavior on missing inputs.

Control flow: `testGetContentSummary` creates `parent`, nested directories `a/b/c`, and one file below the nested path. It then obtains the summary for `parent` and asserts directory count is four and file count is one. `testGetContentSummaryIncorrectPath` creates only the parent and asserts a summary request for missing child `parent/a` throws `FileNotFoundException`.

State and persistence behavior: the test depends on persisted namespace metadata for created directories and a touched file. It verifies that summary traversal sees the whole subtree, including the base directory and descendants, rather than only direct children.

Dependencies and integration points: uses `fs.mkdirs` directly and relies on `touch` helper semantics. It integrates with Ozone filesystem metadata listing/stat functionality through the Hadoop `FileSystem` abstraction.

Risks and test signals: catches off-by-one directory counts, missing leaf files in summary traversal, stale metadata after mkdir/touch, and incorrect exception handling for absent paths. The test does not validate byte length, quota fields, or storage policy fields, so those remain outside its signal.
