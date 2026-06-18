# sources/test-tools/xfstests-bld/fstests-bld/android-compat/valloc.c

Purpose: implements `valloc` for Android using `memalign`.

Important APIs and functions: exports `void *valloc(size_t size)`.

Control flow: calls `memalign(getpagesize(), size)` and returns the allocation.

State and persistence: returns heap memory owned by the caller and freed with normal allocator-compatible free if supported by the platform allocator.

Dependencies and integration: includes `<malloc.h>` and `<unistd.h>`; declared in `android_compat.h`.

Risks: `memalign` portability and free compatibility depend on bionic allocator behavior. No overflow or zero-size special handling is added.

Test signals: callers needing page-aligned memory receive non-null aligned allocations or allocator failures consistent with `memalign`.
