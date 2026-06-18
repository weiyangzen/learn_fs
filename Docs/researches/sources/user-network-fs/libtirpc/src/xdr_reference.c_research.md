# sources/user-network-fs/libtirpc/src/xdr_reference.c

Purpose: `xdr_reference.c` implements XDR helpers for pointed-to objects and nullable recursive pointers.

Important APIs, types, and functions: `xdr_reference` XDRs a required referenced object, allocating it on decode when needed. `xdr_pointer` XDRs a boolean presence discriminator followed by the referenced object only when present.

Control flow: `xdr_reference` allocates and zeroes storage on decode if `*pp` is null, calls the supplied object XDR procedure, and frees/nulls the pointer on `XDR_FREE`. `xdr_pointer` first serializes/deserializes a `bool_t` indicating whether data exists; false clears the pointer and succeeds, true delegates to `xdr_reference`.

State and persistence behavior: No module-global state exists. The only persistent effect is caller pointer allocation during decode and caller pointer nulling during free or absent decode.

Dependencies and integration points: It depends on `rpc/types.h`, `rpc/xdr.h`, and caller-supplied object filters. Generated rpcgen code uses these helpers for linked lists and optional structures.

Risks: `xdr_reference` can leak newly allocated memory if the object procedure fails during decode and callers do not later free. The helper cannot detect graph sharing or cycles by itself; `xdr_pointer` only handles tree-like recursive structures encoded with presence booleans. A null pointer on encode with `xdr_reference` will be passed to the object filter.

Test signals: Tests should cover absent/present pointers, decode allocation, free nulling, recursive list round trips, and failure cleanup conventions.
