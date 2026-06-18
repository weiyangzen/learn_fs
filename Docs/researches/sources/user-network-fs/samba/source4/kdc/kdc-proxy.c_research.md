# sources/user-network-fs/samba/source4/kdc/kdc-proxy.c

## Purpose
`kdc-proxy.c` implements RODC KDC request proxying to writable DC replication partners. When the local RODC cannot answer because it lacks secrets, UDP/TCP request handlers can forward the original Kerberos request to a writable DC and relay the reply.

## Important APIs, Types, And Functions
Public async APIs are `kdc_udp_proxy_send`/`kdc_udp_proxy_recv` and `kdc_tcp_proxy_send`/`kdc_tcp_proxy_recv`. Internal helpers include `kdc_proxy_get_writeable_dcs`, UDP state machine functions (`kdc_udp_next_proxy`, resolve/sendto/recv callbacks), and TCP state machine functions (`kdc_tcp_next_proxy`, resolve/connect/write/read callbacks). State structs keep the event context, KDC pointer, local service port, input/output blobs, proxy candidate list, candidate index, resolved IP, and socket/stream.

## Control Flow
Both UDP and TCP paths first load writable DC candidates from `repsFrom` on the default naming context, then iterate candidates. Each candidate is resolved with DNS-only resolution. UDP creates a connected datagram socket, sends the raw request, arms a receive with `proxy_timeout`, and completes on reply or tries the next candidate on send/receive/resolve failure. TCP builds a 4-byte length-prefixed request, connects to the target port, writes the request, reads a length-prefixed reply, strips the header, and completes.

## State And Persistence Behavior
The file reads persistent replication partner metadata from DSDB `repsFrom` but does not modify DB state. All proxy state is per-`tevent_req` and freed when the request completes.

## Dependencies And Integration Points
It depends on `kdc_server` state, DSDB replication metadata (`dsdb_loadreps`), Samba resolver, tsocket/tstream/tdgram async I/O, packet framing helpers, and tevent NTSTATUS helpers. It is called by `kdc-server.c` only when processing returned `KDC_PROXY_REQUEST` on an RODC.

## Risks
Proxy availability depends on accurate `repsFrom` metadata and DNS resolution. Candidate iteration must not complete before both send and receive paths have handled errors. TCP/UDP framing differs, so length-header handling must stay exact. Timeouts must be bounded to avoid request hangs, and proxying must remain gated to RODCs in the caller.

## Test Signals
Test with no replication partners, unresolvable partners, UDP send failures, UDP timeout then next candidate, TCP connect/write/read failures, successful TCP length stripping, and caller behavior when all candidates fail. RODC integration tests should assert fallback to writable DC for missing-secret AS/TGS paths.
