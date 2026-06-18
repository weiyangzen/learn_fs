# sources/test-tools/cthon04/tools/pmapbrd.c

## Purpose
stress-tests portmapper broadcast RPC by sending repeated `PMAPPROC_CALLIT` broadcasts at a requested packet rate.

## Important APIs, Types, and Functions
Important types are `rmtcallargs`, `rmtcallres`, `XDR`, broadcast `sockaddr_in`, and result callback `resultproc_t`. Key functions are `main()`, `getbroadcastnets()`, `clnt_broadcast_time()`, `xdr_rmtcall_args()`, `xdr_rmtcallres()`, and `eachresult()`.

## Control Flow and State
It opens a UDP socket on port 3300, enables broadcast, discovers a broadcast address with interface ioctls, then loops `count` times calling a custom broadcast routine. That routine XDR-encodes a portmapper CALLIT request, sends it, waits with `select()` for a short timeout, decodes matching replies, and returns `RPC_TIMEDOUT` when no more replies arrive.

## Persistence and Dependencies
state includes static XDR buffers, selected broadcast address, socket binding, RPC auth handle, transaction id, and transient decoded replies. Dependencies: SunRPC headers/libraries, portmapper protocol, UDP sockets, interface ioctls, XDR, `select`, and broadcast-capable network configuration.

## Integration Points, Risks, and Test Signals
Integration is a network/portmapper diagnostic. Risks include old `select(32)` fd limit, raw fd-set casting, only one broadcast address, root/network policy restrictions, and RPC library portability. Signals are repeated `RPC_TIMEDOUT` completions without other client errors and visible broadcast rate output.
