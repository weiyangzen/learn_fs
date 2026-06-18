# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/xdr_reference.c

This file implements pointer/reference XDR helpers: `xdr_reference` and `xdr_pointer`.

`xdr_reference` serializes or deserializes an object reached through a pointer. If the pointed-to storage is NULL during decode, it allocates `size` bytes with `mem_alloc`, zeroes the object, then invokes the supplied XDR procedure. During free, NULL references are ignored, and non-NULL objects are passed to the supplied XDR procedure in `XDR_FREE` mode before being freed and nulled.

`xdr_pointer` adds a boolean presence tag around `xdr_reference`, allowing recursive/tree-like pointer structures to preserve NULL vs non-NULL. It first encodes/decodes `more_data` with `xdr_bool`; if false, it sets the pointer to NULL and returns success. If true, it delegates to `xdr_reference`.

Dependencies are the RPC memory allocation API, `xdr_bool`, and caller-provided object XDR procedures.

Research notes and risks:
- Encode with a NULL pointer and direct `xdr_reference` can call the object procedure with NULL because only decode allocates; callers needing nullable pointers should use `xdr_pointer`.
- Allocation failure is reported with `warn` and returns `FALSE`.
- Free behavior assumes the object XDR procedure can safely free nested allocations before the outer object is freed.
