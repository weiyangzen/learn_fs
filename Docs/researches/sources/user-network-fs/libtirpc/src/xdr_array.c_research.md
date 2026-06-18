# sources/user-network-fs/libtirpc/src/xdr_array.c

Purpose: `xdr_array.c` implements generic XDR helpers for variable-length counted arrays and fixed-length vectors.

Important APIs, types, and functions: `xdr_array` serializes/deserializes arrays addressed by `caddr_t *addrp`, a count pointer, max element count, element size, and element XDR procedure. `xdr_vector` serializes/deserializes a fixed number of statically allocated elements.

Control flow: `xdr_array` first XDRs the element count, rejects counts above `maxsize` or multiplication overflow when not freeing, allocates and zeroes decode storage if `*addrp` is null, then iterates element by element calling `elproc`. On `XDR_FREE`, it calls each element free handler through the same loop and then frees the array. `xdr_vector` simply walks fixed storage and calls the element procedure for each entry.

State and persistence behavior: No module-global state is used. Decode may allocate heap storage with `mem_alloc`; free releases it with `mem_free` and nulls the caller pointer. Fixed vectors never allocate or free their backing storage.

Dependencies and integration points: It depends on `rpc/types.h`, `rpc/xdr.h`, and the caller-supplied element XDR procedures. Generated RPC protocol code uses this for arrays such as gids and rpcbind statistics lists.

Risks: If an element procedure fails during decode after partial allocation, the array remains allocated with partially decoded elements; callers must invoke `XDR_FREE` for cleanup. `xdr_array` does not reject a null encode pointer with nonzero count, so invalid caller state can reach element procedures. Pointer arithmetic uses byte-sized `caddr_t` assumptions.

Test signals: Tests should exercise zero-length arrays, max-count rejection, `UINT_MAX / elsize` overflow rejection, decode allocation, partial element failure followed by free, and fixed-vector round trips.
