# sources/storage-engines/foundationdb/flow/Deque.cpp

## Purpose
`Deque.cpp` contains unit tests for Flow's custom `Deque` container, including normal queue behavior, wraparound at maximum size, and exception safety during growth.

## Important APIs, Types, and Functions
The tests exercise `Deque<T>::push_back`, `pop_front`, `pop_back`, indexing, `front`, `back`, `size`, `empty`, and `max_size`. `RandomlyThrows` is a test helper whose copy and assignment operations randomly throw Flow `success()` errors to stress growth rollback.

## Control Flow
The basic test mutates a deque through pushes and pops and validates remaining values. The queue test uses `std::queue<int, Deque<int>>` with randomized push/pop choices while checking FIFO order. The max-size test fills to capacity after wraparound, validates physical adjacency of `back` and `front`, and expects `std::bad_alloc` on over-capacity push. The exception-safety test retries pushes until they succeed and verifies all stored values.

## State and Persistence Behavior
All state is in-memory container data. There is no persistence.

## Dependencies and Integration Points
The file depends on `flow/Deque.h`, `flow/UnitTest.h`, deterministic randomness, and standard queue adaptation. It validates behavior for Flow subsystems that rely on the custom deque.

## Risks and Edge Cases
The max-size test assumes specific wraparound storage behavior and pointer adjacency. Exception safety is especially important because Flow error throwing during element movement must not corrupt existing deque contents.

## Test Signals
Test case names are `/flow/Deque/12345`, `/flow/Deque/queue`, `/flow/Deque/max_size`, and `/flow/Deque/grow_exception_safety`. `forceLinkDequeTests` ensures linkage.
