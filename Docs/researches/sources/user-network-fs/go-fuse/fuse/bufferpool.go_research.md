## sources/user-network-fs/go-fuse/fuse/bufferpool.go

Purpose: explicit page-aligned buffer reuse to reduce GC overhead while communicating with the FUSE device.

Important APIs/types/functions: `bufferPool` stores `sync.Pool`s indexed by page count and testing counters. `AllocBuffer(size)` rounds up to at least one page and returns a slice with requested length backed by a pooled page-multiple capacity. `FreeBuffer(slice)` returns page-aligned buffers to the corresponding pool. `counters` exposes outstanding allocation counts.

Control flow: allocation computes page count, obtains or creates a pool under lock, gets a backing slice, and slices it to requested size. Free validates capacity/page count and returns the full slice.

State and persistence: in-memory pool state and counters persist for the process.

Dependencies and integration: used by server request handling to bound allocation churn and interacts with `MaxInflightRequestBytes`.

Risks and test signals: wrong rounding or free accounting can cause memory bloat or buffer reuse races. `bufferpool_test.go` covers counters and request handler reuse.
