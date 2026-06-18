# sources/storage-engines/rocksdb/memory/memkind_kmem_allocator.h

Purpose: Declaration of the memkind DAX KMEM memory allocator.

Important APIs/types/functions: `MemkindKmemAllocator`, `kClassName`, `Name`, `IsSupported`, `PrepareOptions`, conditional allocation overrides.

Control flow and state: support is a compile-time check on `MEMKIND`; unsupported builds return a reason string. Allocation methods are compiled only when support exists.

State and persistence behavior: stateless wrapper over memkind allocation APIs.

Dependencies and integration points: `MemoryAllocator::CreateFromString` registry and block cache allocator configuration.

Risks: build-dependent API surface. Runtime availability of desired memory kind is not deeply validated here beyond memkind allocation behavior.

Test signals: conditional parameterized allocator tests cover support and cache integration.
