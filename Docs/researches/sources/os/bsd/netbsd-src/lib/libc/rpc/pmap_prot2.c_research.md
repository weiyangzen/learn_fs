# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot2.c

Read completely: 151 lines.

Implements `xdr_pmaplist()` and `xdr_pmaplist_ptr()` for linked lists of portmapper entries. The XDR representation is a recursive pointer union encoded as a boolean “more elements” flag followed by a `struct pmap`; this implementation unwinds that recursion into a loop and uses `xdr_reference()` per node.

The free path stores the next pointer before freeing the current node so iteration remains valid. `xdr_pmaplist_ptr()` is a compatibility wrapper with a different declared pointer shape.

This is core v2 portmapper list XDR used by `pmap_getmaps()` and legacy pmap dump handling.
