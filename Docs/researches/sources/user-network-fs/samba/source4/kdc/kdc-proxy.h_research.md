# sources/user-network-fs/samba/source4/kdc/kdc-proxy.h

## Purpose
`kdc-proxy.h` declares the async RODC proxy API used by KDC socket handlers to forward Kerberos requests to writable DCs.

## Important APIs, Types, And Functions
It declares `kdc_udp_proxy_send`, `kdc_udp_proxy_recv`, `kdc_tcp_proxy_send`, and `kdc_tcp_proxy_recv`. Both send functions accept a talloc context, tevent context, `struct kdc_server`, local service port, and request blob. Receive functions return an `NTSTATUS` and move the output blob into caller memory.

## Control Flow
The header exposes the standard tevent send/recv pattern. Callers start a proxy request, attach a callback, and in the callback call the matching recv function to obtain the proxied KDC reply or error.

## State And Persistence Behavior
No state is stored in the header. The implementation stores transient per-request state and reads DSDB replication metadata.

## Dependencies And Integration Points
It integrates `kdc-server.c` with `kdc-proxy.c` and depends on Samba's tevent and `DATA_BLOB` conventions plus `struct kdc_server` from the KDC server layer.

## Risks
UDP and TCP send/recv functions must be paired correctly. Callers must retain the input blob for the async lifetime as required by implementation semantics.

## Test Signals
Build and runtime tests should exercise both proxy APIs from UDP and TCP request handling, including successful replies and unavailable-proxy error handling.
