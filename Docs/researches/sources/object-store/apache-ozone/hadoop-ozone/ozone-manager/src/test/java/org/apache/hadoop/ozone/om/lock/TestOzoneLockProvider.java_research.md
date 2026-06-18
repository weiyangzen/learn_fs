# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestOzoneLockProvider.java

Purpose: unit test coverage for `OzoneLockProvider.createLockStrategy(BucketLayout)`, ensuring the configured key path lock and filesystem path flags choose the expected `OzoneLockStrategy` implementation across every `BucketLayout`.

Important APIs/types: `OzoneLockProvider`, `OzoneLockStrategy`, `OBSKeyPathLockStrategy`, `RegularBucketLockStrategy`, `BucketLayout`, and mocked `OzoneManager.getOzoneLockProvider()`. The parameter source enumerates all four boolean combinations of `keyPathLockEnabled` and `enableFileSystemPaths`.

Control flow: `testOzoneLockProvider` stores the parameter flags, loops through `BucketLayout.values()`, builds an `OzoneLockProvider`, and asserts implementation type only for behavior that should be constrained. If key path locking is enabled, `OBJECT_STORE` and legacy-without-filesystem-paths must use OBS key path locking. If key path locking is disabled, all layouts must return the regular bucket strategy.

State and persistence behavior: there is no persistent state; all state is per-test booleans and a Mockito `OzoneManager`. The test guards strategy selection that later affects lock granularity and contention behavior in OM metadata operations.

Dependencies and integration points: integrates with OM bucket layout policy and lock strategy implementations. Uses JUnit 5 parameterized tests and Mockito. Logging emits current flags and layout.

Risks: the test does not assert the positive strategy for every key-path-enabled layout, so FSO or legacy-with-filesystem-paths behavior can change without direct assertion. It also uses `assertInstanceOf` only on selected branches.

Test signals: verifies the expected object-store and legacy/OBS path-lock decisions and the full fallback when key path locking is disabled.
