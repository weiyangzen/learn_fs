# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MoveConstructor.cpp

Purpose: tests that `QueueMap` uses move construction for rvalue values and copy construction for lvalue values.

Important APIs/types/functions: `QueueMapTest_MoveConstructor`, `QueueMap<MinimalKeyType, CopyableMovableValueType>`, `push`, `pop`, keyed `pop`, and copy counter.

Control flow: pushes temporary and lvalue values, pops by FIFO or key, and checks the copy-constructor counter.

State and persistence behavior: in-memory queue/map entries only; static counter records constructor behavior.

Dependencies and integration points: uses `QueueMap`, `MinimalKeyType`, `CopyableMovableValueType`, `cpputils::unique_ref`, and GoogleTest.

Risks and test signals: validates efficient value storage across both pop APIs. It does not test move-only values directly.
