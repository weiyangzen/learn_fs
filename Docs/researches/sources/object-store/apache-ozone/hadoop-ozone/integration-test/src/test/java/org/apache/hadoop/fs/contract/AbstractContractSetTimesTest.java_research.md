# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSetTimesTest.java

Purpose: `AbstractContractSetTimesTest` validates the negative path for `FileSystem.setTimes` on filesystems declaring `SUPPORTS_SETTIMES`. It ensures setting timestamps on a missing file fails.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `Path`, `FileNotFoundException`, JUnit `@BeforeEach`/`@Test`, and AssertJ `fail`. `setup()` calls `skipIfUnsupported(SUPPORTS_SETTIMES)` and initializes `target` under `test/target`.

Control flow: `testSetTimesNonexistentFile` captures the current wall-clock time, calls `getFileSystem().setTimes(target, time, time)` without creating the target, and fails if the call succeeds. It accepts `FileNotFoundException` and passes it to `handleExpectedException`.

State and persistence behavior: this test should not create or mutate any file. Its signal is that metadata update operations do not synthesize missing paths or silently succeed without persistence.

Dependencies and integration points: depends on the contract flag for timestamp support and the concrete filesystem's `setTimes` implementation. It uses the base class exception handling policy.

Risks and test signals: catches filesystems that create placeholder objects on timestamp update, ignore missing paths, or report timestamp support while lacking standard error behavior. It does not test successful modification/access time changes on existing files.
