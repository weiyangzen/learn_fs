# sources/storage-engines/rocksdb/port/win/win_jemalloc.cc

Purpose: plugs jemalloc into Windows RocksDB builds, including optional ZSTD custom allocation and global new/delete replacement.

Important APIs/types/functions: `JemallocAllocateForZSTD`, `JemallocDeallocateForZSTD`, `GetJeZstdAllocationOverrides`, `jemalloc_aligned_alloc`, `jemalloc_aligned_free`, and global `operator new/delete` overloads.

Control flow: only compiles on `OS_WIN` with `ROCKSDB_JEMALLOC`; optional ZSTD hooks compile only with static-linking ZSTD version 5+. New/new[] allocate with `je_malloc` and throw `std::bad_alloc` on failure; delete/delete[] call `je_free`.

State and persistence behavior: no persistence; it changes process allocation behavior when linked.

Dependencies and integration points: consumed by `port_win.h` cacheline allocation helpers and compression code needing ZSTD custom memory hooks.

Risks and test signals: global operator replacement is high blast-radius and must match linker/build assumptions. Allocator, compression, and Windows jemalloc build tests are important.
