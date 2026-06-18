# sources/user-network-fs/rclone/lib/pool/pool.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool.go -->
## sources/user-network-fs/rclone/lib/pool/pool.go

Purpose: implements a deterministic reusable byte-buffer pool with optional mmap allocation and an optional global memory semaphore. It is a lower-level resource manager used by transfer buffering and `pool.RW`.

Important APIs and control flow: `New(flushTime, bufferSize, poolSize, useMmap)` creates a `Pool`, selecting either `make([]byte, size)` or `mmap.Alloc`/`mmap.Free`. `Get` delegates to atomic `GetN(1)`, while `GetN(n)` acquires global memory capacity, removes cached buffers, allocates missing buffers, and retries with exponential sleep on allocation failure. `Put`/`PutN` validate buffer capacity, cache up to `poolSize`, free overflow, release memory quota, update `inUse`, and schedule the flusher. `Flush` frees all cached buffers. `flushAged` periodically frees the minimum idle fill seen during the previous interval.

State, dependencies, and integration: `Pool` protects `cache`, `minFill`, `inUse`, `alloced`, timer flags, and allocator functions with `mu`. `totalMemory` is a package-level `semaphore.Weighted` initialized once from `fs.ConfigInfo.MaxBufferMemory` and counts buffers in active use, not cached buffers. `Global()` lazily creates a standard 1 MiB buffer pool using `fs.GetConfig` and `UseMmap`.

Risks and test signals: returned buffers must have the original capacity or `Put` panics; callers must pair every `Get` with a `Put` to avoid leaked memory-quota permits. `GetN` requests quota for all `n` buffers even if some will come from cache, which limits active use conservatively but means cached memory is not globally counted. Tests cover get/put reuse order, flush aging, mmap paths, unreliable allocator retries, wrong-size panic, and `MaxBufferMemory` limiting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool.go -->
