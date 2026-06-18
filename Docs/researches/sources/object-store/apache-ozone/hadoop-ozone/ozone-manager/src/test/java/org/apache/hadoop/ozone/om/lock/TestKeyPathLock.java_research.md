# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestKeyPathLock.java

Purpose: Tests `OzoneManagerLock.LeveledResource.KEY_PATH_LOCK` concurrency and lock-level ordering constraints.

Important APIs and types: `OzoneManagerLock`, `LeveledResource.KEY_PATH_LOCK`, `LeveledResource.BUCKET_LOCK`, read/write lock acquisition and release, current-lock tracking, `CountDownLatch`, and `GenericTestUtils.waitFor`.

Control flow: `testKeyPathLockMultiThreading` runs same-key and different-key write-lock scenarios. Same-key threads all contend on one key path, increment a shared counter while locked, and record sequential tokens. Different-key threads lock unique keys under one bucket and wait until all have acquired/released enough to show independent locking. Four additional tests acquire key-path read/write locks and assert acquiring higher-level bucket read/write locks is rejected.

State and persistence: all state is in-memory lock maps, per-thread lock tracking, and a shared counter. No persistence.

Dependencies and integration points: protects OM file/key operations that lock path-level resources and enforce hierarchical lock ordering to avoid deadlocks.

Risks and edge cases: same key path must serialize writers; distinct key paths should not block each other globally; lock hierarchy must prevent acquiring a higher-level bucket lock while holding a lower-level key-path lock, for both read and write modes. Thread sleeps and waits can be timing-sensitive.

Test signals: final counter equals `threadCount * iterations`, sequential token list proves same-key serialization, current-lock size is one per different-key thread, latch completion reaches zero, and hierarchy violations throw with a message naming the held key-path lock.
