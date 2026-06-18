<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h

Purpose: This Attractive Chaos header provides macro-based dynamic arrays for C-style code. It is used by directory aggregation to store byte buffers and offsets.

Important APIs: `kvec_t(type)` declares a vector with `n`, `m`, and `a`. Macros initialize, destroy, resize, copy, push, push pointer slots, indexed auto-growth (`kv_a`), pop, delete-by-swap, and inspect size/capacity.

Control flow and state: capacity doubles on push and rounds up on indexed growth. Storage is managed with `realloc` and freed with `free`; vector state is embedded in the caller's struct.

Risks and test signals: allocation failures are not checked by these macros, which can lose the old pointer on `realloc` failure. The macros evaluate some arguments multiple times and are not thread-safe. Tests should focus on append/growth, indexed holes, copy, reset/free patterns, and out-of-memory behavior if wrapped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h -->
