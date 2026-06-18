<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_rmt.c -->
# sources/user-network-fs/libtirpc/src/pmap_rmt.c

Purpose: legacy portmapper remote-call support for IPv4 `PMAPPROC_CALLIT`. The file lets callers ask a remote portmapper to locate a program/version and invoke one procedure in a single UDP RPC call.

Important APIs and functions: `pmap_rmtcall()` builds a UDP client to `PMAPPORT`, fills `struct rmtcallargs` and `struct rmtcallres`, invokes `CLNT_CALL(... PMAPPROC_CALLIT ...)`, returns the contacted service port through `port_ptr`, and resets `addr->sin_port` to zero. `xdr_rmtcall_args()` serializes program/version/procedure plus an opaque argument blob whose length is backpatched after calling the caller-supplied argument XDR routine. `xdr_rmtcallres()` decodes the returned port and then dispatches to the caller-supplied result XDR routine.

Control flow: the public call temporarily mutates the passed `sockaddr_in` to point at the portmapper, creates a UDP client with a fixed three-second retry timeout, performs one RPC call using the user-provided timeout, destroys the client, and restores the input address port field. The XDR argument encoder records the stream position before the length field, emits placeholder length, serializes arguments, computes the byte span, seeks back to overwrite the length, then restores the final position.

State and persistence: no durable state is stored. The only side effect is transient mutation of `addr->sin_port`; assertions require non-null `addr` and `port_ptr`.

Dependencies and integration points: depends on classic SunRPC headers, `clntudp_create`, `CLNT_CALL`, `xdr_reference`, and portmapper protocol constants from `rpc/pmap_prot.h`. It integrates with compatibility callers that still use portmapper rather than rpcbind.

Risks: IPv4/UDP only, legacy portmapper only, and no broadcast implementation in this file despite historical comments. Length backpatching assumes an XDR stream that supports `XDR_GETPOS` and `XDR_SETPOS`. Callers must pass valid XDR procedures and writable result storage.

Test signals: exercise successful `PMAPPROC_CALLIT` against a portmapper-compatible test service, service-not-registered failure, encode/decode with non-empty and empty argument/result payloads, preservation of `addr->sin_port` after failure, and XDR streams that reject seek/backpatch operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/pmap_rmt.c -->
