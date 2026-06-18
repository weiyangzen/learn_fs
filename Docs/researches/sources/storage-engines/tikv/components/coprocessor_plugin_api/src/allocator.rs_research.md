# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/allocator.rs

Purpose: defines a plugin-side global allocator that forwards allocation and deallocation to TiKV’s host allocator, allowing owned Rust values to cross the plugin boundary more safely than with separate allocators.

Important APIs and types: `HostAllocatorPtr`, `HostAllocator`, `AllocFn`, `DeallocFn`, `HostAllocator::new`, `HostAllocator::set_allocator`, and the `GlobalAlloc` implementation.

Control flow: the plugin constructor receives `HostAllocatorPtr` from TiKV and calls `HOST_ALLOCATOR.set_allocator`. Later allocations call the stored host `alloc_fn`; deallocations call `dealloc_fn`. Function pointers are stored atomically.

State and persistence: process-local atomic function pointers; no persistence.

Dependencies and integration: used by the `declare_plugin!` macro, which installs `HostAllocator` as the global allocator outside tests. Depends on the `atomic` crate for `Atomic<Option<fn>>`.

Risks: allocation before `set_allocator` panics via `unwrap`; the macro must set the allocator before constructing plugin objects that allocate. Function pointer signatures and Rust `Layout` ABI must match host and plugin. Relaxed loads are used after SeqCst stores, relying on initialization ordering in the constructor path.

Test signals: unit test asserts that `Atomic<Option<AllocFn>>` is lock-free.
