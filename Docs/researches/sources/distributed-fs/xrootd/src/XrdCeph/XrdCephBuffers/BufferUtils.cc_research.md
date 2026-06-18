# sources/distributed-fs/xrootd/src/XrdCeph/XrdCephBuffers/BufferUtils.cc

Purpose: implements shared Ceph buffer utilities: extent math, extent holder aggregation, debug logging lock, and RAII nanosecond timer.

Important APIs/types/functions: global `cephbuf_iolock` under debug; `Extent::in_extent`, `isContiguous`, `allInExtent`, `someInExtent`, `containedExtent`, comparison operators; `ExtentHolder` constructors/destructor, `push_back`, `asExtent`, byte accounting, sorting/copy helpers; `Timer_ns` constructor/destructor.

Control flow: extents model half-open ranges `[begin,end)`. `ExtentHolder::push_back` maintains aggregate begin/end as extents are added. Sorting returns by offset and then end. Timer captures start time and writes elapsed nanoseconds on destruction.

State and persistence: utility objects are in-memory only. `cephbuf_iolock` serializes debug log writes process-wide.

Dependencies and integration points: used by Ceph buffer algorithms, IO adapters, and readv adapters. Depends on STL containers, chrono, mutex, and algorithm.

Risks: `Extent::in_extent` uses `pos > begin()` rather than `pos >= begin()`, excluding the first byte, unlike other methods. `ExtentHolder(const ExtentContainer&)` iterates over `m_extents` instead of the input `extents`, so it copies nothing; this affects readv conversion shortcuts. `convert` users need sorted input, but not all constructors enforce sorting.

Test signals: boundary tests for extent inclusion, contained subranges, holder copy construction, bytes missing with overlaps/gaps, sorting, and timer value update.
