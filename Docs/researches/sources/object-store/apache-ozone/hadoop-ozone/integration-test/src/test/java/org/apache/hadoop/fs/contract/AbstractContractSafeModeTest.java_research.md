# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSafeModeTest.java

Purpose: `AbstractContractSafeModeTest` validates the Hadoop `SafeMode` interface lifecycle on filesystems that implement it. It is a compact test of GET, ENTER, LEAVE, and FORCE_EXIT semantics.

Important APIs/types/functions: extends `AbstractFSContractTestBase`; uses `FileSystem`, `SafeMode`, `SafeModeAction`, and AssertJ. Helper `verifyAndGetSafeModeInstance` asserts the filesystem instance implements `SafeMode` before casting.

Control flow: `testSafeMode` retrieves the filesystem, verifies the interface, then calls `setSafeMode(GET)` expecting false before entry. It calls `ENTER` and expects true, calls `GET` again and expects true, then calls `LEAVE` and `FORCE_EXIT`, both expected to return false after safe mode is off.

State and persistence behavior: the test mutates cluster/filesystem safe mode state through the interface. It assumes the initial state is off and leaves the filesystem off at the end. No files are created or deleted.

Dependencies and integration points: integrates the generic Hadoop `SafeMode` interface with the concrete filesystem. It does not use a path-capability flag, so subclasses should include it only when the filesystem supports the interface and safe mode operations are isolated enough for tests.

Risks and test signals: catches missing `SafeMode` implementation, inverted boolean returns, failure to persist safe mode state between actions, and failure to exit. Risk is global state leakage if a failing test leaves safe mode enabled.
