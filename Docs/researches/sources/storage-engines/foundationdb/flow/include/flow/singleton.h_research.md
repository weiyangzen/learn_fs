# sources/storage-engines/foundationdb/flow/include/flow/singleton.h

## Purpose
This header provides `crossbow::singleton`, a policy-based singleton holder originally from the Crossbow code used by FoundationDB. It abstracts allocation, lifetime, and locking policies so a type can be lazily constructed, optionally destroyed at process exit, and accessed through static `instance()` or pointer-like wrapper operators.

## Important APIs, Types, and Functions
Creation policies are `create_static<T>`, `create_using_new<T>`, `create_using_malloc<T>`, and `create_using<T, allocator>`. Lifetime policies are `default_lifetime<T>`, `phoenix_lifetime<T>`, and `infinite_lifetime<T>`, with `lifetime_traits` controlling whether recreation is supported. `no_locking` implements a mutex-like no-op policy. On Windows, `WinLockGuard` and `MUTEX_TYPE` wrap a Win32 `HANDLE`; elsewhere locking defaults to `std::mutex` and `std::lock_guard<Mutex>`. The main template is `singleton<Type, Create, LifetimePolicy, Mutex>`.

## Control Flow
`singleton::instance()` performs lazy double-checked initialization. If `instance_` is null, it acquires `mutex_`, checks again, handles dead-reference state, creates the object through `Create::create()`, and registers `destroy()` through the selected lifetime policy. `destroy()` calls `Create::destroy(instance_)`, nulls the pointer, and marks `destroyed_`. `destroy_instance()` explicitly destroys the object under lock and warns that it must not be called while multithreaded. Operator overloads call `instance()` on demand and return pointer/reference access to the stored object.

## State and Persistence Behavior
All state is process-local static template state: `destroyed_`, `instance_`, and `mutex_`. No persisted state is written. `default_lifetime` uses `std::atexit`, so destruction order relative to other global state matters. `phoenix_lifetime` permits recreation after destruction if the creation policy supports it; `infinite_lifetime` intentionally never schedules destruction.

## Dependencies and Integration Points
The header uses the C++ standard library for allocation, mutexes, assertions, and `std::atexit`. On Windows it depends on `Windows.h` and `std::system_error`. It is isolated under namespace `crossbow` and can be included by any component that wants a configurable singleton rather than function-local static construction.

## Risks
The double-checked locking pattern depends on correct static pointer visibility and may be less robust than C++11 function-local statics. Windows `WinLockGuard` creates a mutex in its constructor every time it is used and stores it through the reference, which is unusual and can leak handles. `destroy_instance()` is explicitly unsafe under concurrent use. `create_static` uses a custom union for alignment and should be revisited if used with over-aligned types. Dead-reference handling can throw under `default_lifetime`.

## Test Signals
Unit tests should cover one-time construction, explicit destruction, post-destruction access under each lifetime policy, custom allocator creation/destruction, and no-locking use in single-threaded contexts. Threaded tests should stress concurrent `instance()` calls and confirm only one object is constructed. Windows builds need coverage for the `WinLockGuard` branch.
