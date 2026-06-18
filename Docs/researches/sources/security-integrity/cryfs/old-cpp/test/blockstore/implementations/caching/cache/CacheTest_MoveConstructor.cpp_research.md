# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_MoveConstructor.cpp

Purpose: tests that `Cache` uses move construction when possible and only copies when an lvalue is pushed.

Important APIs/types/functions: `CacheTest_MoveConstructor`, `Cache<MinimalKeyType, CopyableMovableValueType, 100>`, `push`, `pop`, and `CopyableMovableValueType::numCopyConstructorCalled`.

Control flow: resets copy counter, pushes either a temporary or lvalue, pops it, touches the value to prevent optimization, and asserts copy count.

State and persistence behavior: cache holds in-memory key/value entries; test state is the static copy counter.

Dependencies and integration points: uses `Cache`, minimal test key/value types, `cpputils::unique_ref`, and GoogleTest.

Risks and test signals: verifies efficient ownership transfer. It does not inspect move-constructor count, only absence/presence of copies.
