# sources/user-network-fs/samba/source3/rpc_server/mdssvc/dalloc.h

## Purpose
This header declares the talloc-backed dynamic typed object store used by mdssvc. It documents the intended object patterns: ordered sets, dictionaries represented as alternating key/value elements, and nested `DALLOC_CTX` containers.

## Important APIs, Types, And Functions
`struct dalloc_ctx` is opaque and typedefed as `DALLOC_CTX`. The creation macros are `dalloc_new(mem_ctx)` for a generic `DALLOC_CTX` and `dalloc_zero(mem_ctx, type)` for typedefed dalloc containers named as `type`. `dalloc_add_copy()` copies a scalar into the store with a type-name tag, while `dalloc_add()` appends an existing talloc child after type validation. The public functions expose indexed retrieval, key lookup, size/name/object inspection, string append, and debug dumping.

## Control Flow
Callers build dalloc trees by allocating a parent context, appending typed scalars or child containers, then retrieving by paths like `"DALLOC_CTX", index, "uint64_t", index`. The header's examples establish the convention that passing `"DALLOC_CTX"` to `dalloc_get()` or `dalloc_value_for_key()` means "descend into this nested object" rather than return the container itself.

## State And Persistence
The header itself has no runtime state. It defines ownership expectations: all stored objects are talloc-managed, and appended non-copied objects must already be children with the expected talloc name.

## Dependencies And Integration Points
It includes talloc and is included by `marshalling.h`, `dalloc.c`, and mdssvc code that needs dynamic Spotlight value containers. It intentionally exposes `_dalloc_new()` and `_dalloc_add_talloc_chunk()` for macro implementation, while callers should normally use the typed macros.

## Risks And Test Signals
The main API risk is that varargs paths and macro type names are unchecked by the compiler and can fail only at runtime. The `dalloc_zero` name is slightly misleading because it allocates a `DALLOC_CTX`-backed object named after the requested typedef, not an arbitrary zeroed C struct. Test signals are compile-time use from C callers, macro type-name correctness, nested retrieval examples from the header comment, and ABI consistency for the opaque typedef.
