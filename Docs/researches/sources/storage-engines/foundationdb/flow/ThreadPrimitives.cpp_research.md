<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ThreadPrimitives.cpp -->
# sources/storage-engines/foundationdb/flow/ThreadPrimitives.cpp
- Purpose: Implements low-level thread primitives declared in `ThreadPrimitives.h`.
- Important APIs/types/functions: `Event::set`, `Event::block`, `Mutex::Mutex`, `Mutex::~Mutex`, `Mutex::enter`, and `Mutex::leave`.
- Control flow: `Event` delegates to an internal latch: `set()` counts down and `block()` waits. On Windows-oriented mutex implementation, the constructor allocates and initializes a `CRITICAL_SECTION`; enter/leave call the corresponding Win32 APIs; destructor deletes and frees it.
- State and persistence behavior: State is in each primitive instance. No persistence. `Mutex::impl` is heap allocated to keep platform implementation details out of the header.
- Dependencies and integration points: Depends on `ThreadPrimitives.h` and Win32 critical-section APIs when `_WIN32` is active. Used by Flow components that need blocking synchronization outside actor scheduling.
- Risks: The displayed mutex implementation uses `CRITICAL_SECTION`; non-Windows builds must rely on header/platform conditional definitions being compatible. Heap allocation makes construction/destruction failure and ownership simple but adds allocation cost.
- Test signals: Coverage is indirect through trace writer barriers, thread helpers, and other synchronization users. Dedicated tests should verify event one-shot wake behavior and mutex mutual exclusion on supported platforms.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/ThreadPrimitives.cpp -->
