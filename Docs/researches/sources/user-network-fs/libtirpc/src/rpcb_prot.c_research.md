<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_prot.c -->
# sources/user-network-fs/libtirpc/src/rpcb_prot.c

Purpose: XDR routines for rpcbind protocol data structures and rpcbind remote-call payloads.

Important APIs and functions: `xdr_rpcb()`, `xdr_rpcblist_ptr()`, `xdr_rpcblist()`, `xdr_rpcb_entry()`, `xdr_rpcb_entry_list_ptr()`, `xdr_rpcb_rmtcallargs()`, `xdr_rpcb_rmtcallres()`, and `xdr_netbuf()`.

Control flow: simple structures serialize fixed integers and bounded strings. Linked-list functions avoid recursive `xdr_pointer` traversal by looping over presence booleans and serializing nodes through `xdr_reference`; free mode saves the next pointer before freeing the current node. Remote-call argument XDR writes program/version/procedure, backpatches the argument length after invoking the provided argument XDR callback, and restores the stream position. Remote-call result XDR reads the universal address, result length, then calls the provided result decoder.

State and persistence: no global state. Decode/free operations allocate or free strings, linked-list nodes, netbuf buffers, and callback-owned payloads through XDR helpers.

Dependencies and integration points: used by `rpcb_clnt.c` for rpcbind requests and by rpcbind-compatible services. Depends on `RPC_MAXDATASIZE` bounds and callback XDR procedures.

Risks: `xdr_rpcb_rmtcallargs()` is intended for encode direction and assumes positional XDR support. `xdr_netbuf()` serializes `maxlen` first and rejects values above `RPC_MAXDATASIZE`; malformed data can still allocate up to that limit. Non-recursive freeing code is subtle and should not be casually refactored.

Test signals: rpcbind map encode/decode/free, long string rejection, multi-node list decode/free without recursion, remote-call argument length backpatch accuracy, result callback invocation, and netbuf maxlen/len boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_prot.c -->
