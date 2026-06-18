# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OzoneLockProvider.java

Purpose: `OzoneLockProvider` chooses a concrete key lock strategy based on configuration and bucket layout.

Important APIs and types: The constructor stores `keyPathLockEnabled` and `enableFileSystemPaths`. `createLockStrategy(BucketLayout bucketLayout)` returns either `OBSKeyPathLockStrategy` or `RegularBucketLockStrategy`.

Control flow: If key-path locking is enabled, object-store buckets use `OBSKeyPathLockStrategy`. Legacy buckets also use it when filesystem paths are disabled, covering old pre-created object-store-like legacy buckets. All other cases fall back to regular bucket locking.

State and persistence behavior: State is two configuration booleans. No persistence is involved.

Dependencies and integration points: Request handlers use the selected strategy to lock keys under different bucket layouts. It depends on `BucketLayout` and lock strategy implementations.

Risks and test signals: Misclassification changes concurrency and correctness for key operations. Tests should cover all bucket layouts with both booleans, especially legacy buckets under filesystem-path enabled/disabled configs, and verify the selected strategy's locking behavior.
