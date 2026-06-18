# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/MutexPoolLockIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/lock/MutexPoolLock.h`.

Important APIs and types: Includes the mutex-pool lock public header.

Control flow: No runtime test cases are declared.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards an RAII lock wrapper used with pooled mutexes.

Risks: Compile-only coverage cannot catch deadlock, unlock, or keyed mutex selection bugs.

Test signals: Successful direct header compilation.
