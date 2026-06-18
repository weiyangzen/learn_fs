# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_prot.h

Purpose: `pmap_prot.h` defines the legacy portmapper v2 protocol constants, mapping structs, list structs, and XDR routines.

Important APIs, types, and functions: It defines `PMAPPORT`, `PMAPPROG`, `PMAPVERS`, procedure numbers `PMAPPROC_*`, `V2FIRST`, `struct pmap`, `struct pmaplist`, `xdr_pmap`, `xdr_pmaplist`, and `xdr_pmaplist_ptr`.

Control flow: Portmapper procedures register, unregister, resolve, dump, or indirectly call registered services using `struct pmap` tuples of program, version, protocol, and port.

State and persistence behavior: The header only defines wire structures. Mapping persistence lives in the portmapper/rpcbind service.

Dependencies and integration points: It is included by portmapper clients, servers, and `rpc.h`. `pmap_rmt.h` covers the CALLIT argument/result wrappers.

Risks: The protocol is bound to TCP/UDP port numbers and does not handle transport-independent addresses. The comment notes `PMAPPROC_CALLIT` is quiet on missing registrations, which complicates diagnostics. Linked list XDR must avoid leaks on partial decode failure.

Test signals: Tests should verify XDR of individual maps and map lists, procedure constants, dump/free behavior, and rpcbind compatibility mode.
