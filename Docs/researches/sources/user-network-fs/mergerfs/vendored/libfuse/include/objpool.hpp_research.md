<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp

Purpose: `ObjPool<T,Allocator,ShouldPool>` is a thread-safe object pool for nothrow-destructible objects that are at least large enough to overlay pool metadata. It supports variable allocation sizes for flexible-array-style objects.

Important APIs and flow: `alloc` and `alloc_size` pop a node with sufficient allocation size or allocate aligned memory, then placement-new a `T`. `free` and `free_size` run the destructor and either push the memory back onto the free list or deallocate it according to `ShouldPool`. `clear` frees all pooled nodes, `size` returns the current pool count, and `gc` releases about 10 percent, at least one node.

State and integration: the pool stores a singly linked free list protected by `mutex_t`, plus an atomic count for observation. It uses `DefaultAllocator` with aligned `operator new/delete` unless customized. It can back FUSE request/message buffers.

Risks and test signals: `free_size` trusts the caller-provided size, and `to_node` overlays metadata on object memory after destruction. Constructors that throw are handled, but only if allocation metadata is correct. Tests should cover reuse by size, non-pooled predicate deallocation, GC, clear during no live objects, constructor exceptions, and concurrent alloc/free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp -->
