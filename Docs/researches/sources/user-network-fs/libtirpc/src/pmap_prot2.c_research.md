## sources/user-network-fs/libtirpc/src/pmap_prot2.c

Purpose: Implements XDR for linked lists of legacy portmapper records.

Important APIs and control flow: `xdr_pmaplist` encodes/decodes/frees a `struct pmaplist **` as an XDR recursive optional list but implements the recursion iteratively. Each loop emits or reads a boolean `more_elements`; when true it uses `xdr_reference` to process the current node's `struct pmap` with `xdr_pmap`, then advances to `pml_next`. In `XDR_FREE`, it saves the next pointer before freeing the current node. `xdr_pmaplist_ptr` is a compatibility wrapper with a historical pointer signature.

State and persistence: No static state. Decode allocates list nodes through XDR reference handling; free releases them.

Dependencies and integration: Used by `pmap_getmaps` and exported ABI.

Risks and test signals: Pointer casting in `xdr_pmaplist_ptr` is compatibility-sensitive. Tests should cover empty list, multi-node encode/decode/free, malformed boolean streams, and leak-free cleanup after partial decode failure.
