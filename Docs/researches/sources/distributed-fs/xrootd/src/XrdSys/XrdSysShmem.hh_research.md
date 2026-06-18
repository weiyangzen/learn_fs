# sources/distributed-fs/xrootd/src/XrdSys/XrdSysShmem.hh

Purpose: provides header-only POSIX shared-memory helpers for creating, opening, mapping, and constructing arrays in shared memory.

Important APIs/types/functions: `XrdSys::shm_error` carries `errcode` and `errmsg`. `XrdSys::shm::create()`, templated `get<T>()`, templated `make_array<T>()`, variadic `make_array<T, Args...>()`, and private `map_shm()` are the core API.

Control flow: `create()` calls `shm_open(O_CREAT|O_RDWR)`, `ftruncate()`, `fstat()`, maps with `mmap(MAP_SHARED)`, closes the descriptor, and returns pointer/size. `get<T>()` opens an existing object, stats, maps, closes, and casts the pointer. `make_array()` creates a block then placement-news `count` objects into the mapped region.

State and persistence: the POSIX shared memory object persists by name until unlinked outside this helper. The mapping persists in the process until callers `munmap()` it; this header provides no unmap/unlink/destroy helper.

Dependencies and integration: uses POSIX `shm_open`, `ftruncate`, `fstat`, `mmap`, `close`, C++ tuples/strings, and placement new. It is suitable for XRootD components that need process-shared counters or tables.

Risks: file descriptors are not closed on several exception paths after `shm_open()`. `create()` ignores `EINVAL` from `ftruncate()`, then trusts the existing object size, which may differ from requested size. The variadic `make_array` uses `std::forward<Args...>(args...)`, which is not the usual forwarding form and may not compile as intended. No destructor calls are provided for objects constructed in shared memory.

Test signals: create/get round trip, existing object resize behavior, mapping failure cleanup, typed array construction, and caller-side `munmap()`/`shm_unlink()` lifecycle tests.
