# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemnobs.c

Minimal no-backing-store memory backend. It assumes all working memory can be obtained directly from `malloc`.

Small and large allocations map to `malloc/free`. `jpeg_mem_available()` always returns `max_bytes_needed`, so the system-independent memory manager should never request backing store. If backing store is still opened, `jpeg_open_backing_store()` raises `JERR_NO_BACKING_STORE`.

`jpeg_mem_init()` returns zero because the `max_memory_to_use` limit is ignored by this backend; termination has no work.
