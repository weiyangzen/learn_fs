<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java

Purpose: Unit tests for `AuthorizerLockImpl`, the multitenant authorizer lock abstraction backed by stamped locking semantics.

Important APIs/types/functions: Tests call `tryReadLock`, `unlockRead`, `tryWriteLock`, `unlockWrite`, `tryWriteLockInOMRequest`, `unlockWriteInOMRequest`, `isWriteLockHeldByCurrentThread`, `tryWriteLockThrowOnTimeout`, `tryOptimisticReadThrowOnTimeout`, and `validateOptimisticRead`.

Control flow: `testStampedLockBehavior` validates normal unlock, bad stamp exceptions, concurrent read locks, write exclusion while reads are held, write exclusivity, and read exclusion while write is held. Other tests verify write lock can be released by another thread for OM request flow, follower-side unlock without prior lock does not throw, thread-local write lock detection only tracks OM-request write locks, and optimistic reads remain valid across reads but fail or invalidate across writes.

State and persistence behavior: No persistence. Tests observe in-memory lock stamps, timeout results, and thread-local lock-held state.

Dependencies and integration points: Protects behavior used by OM multitenancy authorizer update paths where preExecute and validate/update phases may happen on different threads or leaders/followers.

Risks: Tests use short timeout values and thread start without join in one case, so rare scheduling issues could hide release timing. They do not test high contention or interruption behavior.

Test signals: Passing confirms stamped-lock semantics, graceful follower unlock, OM-request thread-local tracking, and optimistic-read invalidation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestAuthorizerLockImpl.java -->
