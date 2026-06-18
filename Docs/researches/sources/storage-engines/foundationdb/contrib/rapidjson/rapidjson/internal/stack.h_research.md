# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/stack.h

Purpose: `internal::Stack` is RapidJSON's type-unsafe growable byte stack used for parser stacks, writer nesting levels, memory buffers, regex states, and temporary construction storage.

Important APIs and types: The template `Stack<Allocator>` exposes constructor, destructor, optional C++11 move operations, `Swap`, `Clear`, `ShrinkToFit`, `Reserve<T>`, `Push<T>`, `PushUnsafe<T>`, `Pop<T>`, `Top<T>`, `End<T>`, `Bottom<T>`, `HasAllocator`, `GetAllocator`, `Empty`, `GetSize`, and `GetCapacity`.

Control flow: Memory allocation is lazy. The first expansion creates an owned allocator if none was supplied and allocates `initialCapacity_`. Later expansions grow capacity by 1.5x or to the exact needed size. `Resize()` uses allocator `Realloc` and restores the top pointer from the saved size. `ShrinkToFit()` frees memory completely when empty.

State and persistence behavior: State is allocator pointers plus raw `char*` base/top/end. It owns memory allocated through the allocator and may own the allocator itself. No persistence exists, but many higher-level objects rely on stack memory lifetime.

Dependencies and integration points: It includes `allocators.h` and `swap.h`. It underpins `MemoryBuffer`, `Writer` level state, `Reader` parse state, regex compilation/search, and pointer/document internals.

Risks: It is type-unsafe and does not run destructors for stored objects. Alignment depends on allocator behavior and caller usage. `PushUnsafe()` requires a prior successful reserve. Copying is disabled; move support depends on feature macros.

Test signals: Cover lazy allocation, growth, typed push/pop/top/bottom, reserve plus unsafe push, clear versus shrink, allocator ownership, swap, move construction/assignment when enabled, and integration with memory buffers and writer nesting.
