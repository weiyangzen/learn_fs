# sources/user-network-fs/libtirpc/tirpc/rpc/pmap_rmt.h

Purpose: `pmap_rmt.h` defines client-side argument/result wrappers and XDR routines for portmapper remote-call service.

Important APIs, types, and functions: It defines `struct rmtcallargs`, `struct rmtcallres`, `xdr_rmtcall_args`, and `xdr_rmtcallres`.

Control flow: The caller supplies target program/version/procedure, argument XDR routine and pointer, result XDR routine and pointer, and receives the service port plus decoded results from a portmapper-mediated UDP call.

State and persistence behavior: The structures carry caller-owned pointers and XDR function pointers. No persistent state is declared.

Dependencies and integration points: It complements `pmap_clnt.h` and `pmap_prot.h`, and is used by `pmap_rmtcall`/broadcast implementations.

Risks: XDR of embedded opaque args/results depends on correct function pointers and length accounting. Remote call service uses null auth and quiet failure behavior. Pointer-bearing structs are not raw wire structs; they are helper representations for XDR routines.

Test signals: Tests should cover encoded argument length calculation, result length decode, bad XDR procedure failure, port output assignment, and missing-registration behavior through portmapper.
