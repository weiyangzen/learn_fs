# sources/storage-engines/foundationdb/flow/include/flow/FastRef.h

## Purpose
`FastRef.h` defines Flow's intrusive reference-counting base classes and `Reference<T>` smart pointer wrapper.

## Important APIs, Types, And Functions
Important types are `ThreadSafeReferenceCounted`, `ThreadUnsafeReferenceCounted`, `ReferenceCounted` macro alias, free `addref()`/`delref()`, `Reference<P>`, `makeReference()`, equality operators, and `Traceable<Reference<T>>`.

## Control Flow
Objects start with reference count one. `Reference` constructors add references except when taking ownership from raw pointers; destructors call `delref()`. Move transfers the pointer. Assignment increments the new pointer before releasing the old pointer. `extractPtr()` hands ownership to the caller.

## State And Persistence Behavior
Reference count state lives inside each pointee. Thread-safe mode uses an atomic count and only guarantees concurrent add/del safety, not object data safety. `Reference` itself stores only a raw pointer.

## Dependencies And Integration Points
It depends on atomics, `Traceable`, and Swift support. It is the standard ownership mechanism for Flow interfaces such as files, connections, thread pools, histograms, random generators, and rate controls.

## Risks And Edge Cases
No virtual destructor is provided by the base; polymorphic subclasses need their own virtual destructor. `setPtrUnsafe()` and `extractPtr()` can break ownership invariants. Thread-safe reference counting does not synchronize access to object fields. Raw-pointer constructor assumes ownership of one existing reference.

## Test Signals
Tests should cover copy/move/assignment/destruction, upcast construction, `extractPtr()`, `castTo()`, sole-owner/debug counts, concurrent add/del in thread-safe builds, and polymorphic deletion.
