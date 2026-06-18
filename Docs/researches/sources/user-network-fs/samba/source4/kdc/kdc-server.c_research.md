# sources/user-network-fs/samba/source4/kdc/kdc-server.c

## Purpose
`kdc-server.c` provides the shared UDP/TCP socket server for KDC and kpasswd services. It receives Kerberos PDUs, calls a service-specific `kdc_process_fn_t`, sends replies, and invokes RODC proxying when the processor reports `KDC_PROXY_REQUEST`.

## Important APIs, Types, And Functions
The exported API is `kdc_add_socket`. Internal structs model TCP connections/calls and UDP calls. Important callbacks are `kdc_udp_call_loop`, UDP proxy/send completion, `kdc_tcp_accept`, `kdc_tcp_call_loop`, TCP proxy/write completion, and `kdc_proxy_unavailable_error`.

## Control Flow
`kdc_add_socket` creates a `kdc_socket`, binds TCP unless `udp_only`, always binds UDP, creates send queues, and starts the UDP receive loop. UDP receives one datagram, calls `process(..., datagram=1)`, drops errors, proxies on `KDC_PROXY_REQUEST` if the KDC is an RODC, or queues a datagram reply. TCP accepts a stream, wraps it in tstream, reads length-prefixed PDUs, strips the 4-byte header before processing, writes a new 4-byte length header plus reply, then starts the next read. If proxying fails, both UDP and TCP can synthesize `KRB5KDC_ERR_SVC_UNAVAILABLE`.

## State And Persistence Behavior
The file stores transient socket, connection, queue, call, and packet state under talloc parents. It does not persist configuration or directory data. Long-lived state is `struct kdc_socket` and `struct kdc_udp_socket` attached to `struct kdc_server`.

## Dependencies And Integration Points
It depends on Samba process model, tsocket/tdgram/tstream, packet helpers, loadparm socket options, `kdc-server.h` state, `kdc-proxy.h`, and service processors such as Heimdal KDC processing or kpasswd processing. It is used by both `kdc-heimdal.c` and `kdc-service-mit.c`.

## Risks
Length-header arithmetic and pointer adjustment on TCP input must remain correct. UDP receive loop restarts even after allocation/process failures; termination only happens if a new receive cannot be scheduled. Proxying must be rejected when not on an RODC. Generated unavailable errors require a valid Kerberos context and allocation. TCP callbacks intentionally terminate connections on unexpected direct recv/send handlers.

## Test Signals
Signals include UDP and TCP KDC/kpasswd traffic, multiple TCP PDUs on one connection, malformed/short TCP PDUs from packet framing tests, proxy success/failure, unavailable error generation, bind failures, UDP-only wildcard/interface binding, and memory/error-path coverage under socket-wrapper.
