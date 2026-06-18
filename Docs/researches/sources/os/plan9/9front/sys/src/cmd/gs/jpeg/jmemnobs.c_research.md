# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemnobs.c

Purpose: minimal no-backing-store memory backend.

Important behavior:
- Assumes all working memory can be obtained directly from `malloc`.
- Small and large allocations map to `malloc/free`.
- `jpeg_mem_available()` always returns `max_bytes_needed`, so the system-independent manager should never request backing store.
- `jpeg_open_backing_store()` raises `JERR_NO_BACKING_STORE` if backing store is requested anyway.
- `jpeg_mem_init()` returns zero because `max_memory_to_use` is ignored.
- `jpeg_mem_term()` has no cleanup work.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`.
