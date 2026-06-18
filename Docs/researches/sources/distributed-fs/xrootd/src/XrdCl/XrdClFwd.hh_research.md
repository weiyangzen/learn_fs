# sources/distributed-fs/xrootd/src/XrdCl/XrdClFwd.hh

## Purpose
`XrdClFwd.hh` implements a shared forwardable value wrapper for operation pipelines. It allows a value to be allocated lazily, assigned later, shared across operation objects, and dereferenced only after it becomes valid.

## Important APIs, Types, And Functions
`FwdStorage<T>` owns raw aligned storage in a union and a `T *ptr` that is null until construction. It supports construction and assignment from `const T&` and `T&&`, using placement new. Its destructor calls `T`'s destructor only when `ptr` is set. `Fwd<T>` protected-inherits `std::shared_ptr<FwdStorage<T>>`, default-allocates empty storage, supports copy/move sharing, assignment, `operator*`, `operator->`, and `Valid`. `make_fwd<T>` creates a shared storage object with forwarded constructor arguments.

## Control Flow
An operation can create or receive a `Fwd<T>` before the value exists. Later assignment constructs `T` in the storage. Dereference checks `ptr` and throws `std::logic_error` if no value has been assigned.

## State And Persistence Behavior
State is heap-allocated shared storage with manual object lifetime. Copies of `Fwd<T>` point to the same storage, so assignment through one wrapper makes the value visible through the others. No disk persistence exists.

## Dependencies And Integration Points
The wrapper depends on `<memory>` and `<stdexcept>`. It is used by operation/pipeline code to pass results between asynchronous operation stages without requiring default-constructible result types.

## Risks And Test Signals
Repeated assignment calls placement new over an already constructed object without destroying the previous value, which is only safe if higher-level code assigns once. Tests should cover unassigned dereference exceptions, move-only values, shared visibility, destructor execution, and potential repeated-assignment leaks for non-trivial `T`.
