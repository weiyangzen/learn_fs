# sources/storage-engines/leveldb/util/no_destructor.h

## Purpose
Provides `NoDestructor<T>`, a wrapper for function-local or static objects whose destructor should never run. LevelDB uses this pattern for intentionally leaked process-lifetime singletons where shutdown ordering is risky or unnecessary.

## Important APIs, Types, And Functions
The templated constructor perfect-forwards arguments into placement-new storage. `get()` returns an `InstanceType*` by reinterpreting the aligned byte storage. Copy construction and assignment are deleted. Static assertions verify storage size, standard layout, and alignment assumptions.

## Control Flow
Construction performs compile-time validation and then constructs `InstanceType` in `instance_storage_`. Destruction of `NoDestructor` is defaulted and does not call the contained object's destructor because the object is not a direct data member.

## State And Persistence Behavior
The contained instance lives in the wrapper's inline storage for the lifetime of the wrapper. For static wrappers, the constructed object persists until process exit without destructor side effects. There is no file or database persistence.

## Dependencies And Integration Points
It depends on `<type_traits>`, `<utility>`, `<cstddef>`, placement new, and C++17 type traits. It integrates with `no_destructor_test.cc`, which verifies constructor forwarding and destructor suppression.

## Risks And Edge Cases
This intentionally leaks destructor behavior, so it is inappropriate for objects that must flush data, release locks, or unregister external resources. `get()` exposes a raw mutable pointer and relies on callers to respect initialization and lifetime. The alignment static assertions are important because the implementation uses a char array rather than `std::aligned_storage`.

## Test Signals
The tests use a type whose destructor aborts, so success proves the destructor is not called for stack or static wrappers. Constructor argument values are checked to catch forwarding or storage mistakes.
