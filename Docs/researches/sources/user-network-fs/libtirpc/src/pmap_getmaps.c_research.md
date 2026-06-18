## sources/user-network-fs/libtirpc/src/pmap_getmaps.c

Purpose: Implements `pmap_getmaps`, retrieving the full legacy portmapper map list from a host.

Important APIs and control flow: The function asserts a non-null IPv4 address, sets its port to `PMAPPORT`, creates a TCP client with `clnttcp_create`, calls `PMAPPROC_DUMP` with `xdr_pmaplist` and a 60-second timeout, prints RPC errors on failure, destroys the client, resets the caller address port to zero, and returns the decoded linked list head.

State and persistence: No local persistent state. The returned `pmaplist` is caller-owned XDR-allocated data.

Dependencies and integration: Uses legacy TCP client compatibility, pmap protocol XDR, and `clnt_perror`.

Risks and test signals: Mutates the input address port temporarily. Tests should cover successful dump/free, RPC failure logging, client creation failure, address port restoration, and caller ownership of returned list.
