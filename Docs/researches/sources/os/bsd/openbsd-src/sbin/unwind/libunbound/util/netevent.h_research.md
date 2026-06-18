# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/netevent.h

Declares the public and test-visible interface for the event networking layer implemented by `netevent.c`. The header documents the communication model: per-thread `comm_base`, UDP sockets, TCP accept sockets with preallocated handlers, TCP/HTTP/local/raw handlers, timers, signals, and temporary `comm_reply` structures passed to callbacks.

Defines callback error/status codes: `NETEVENT_NOERROR`, `NETEVENT_CLOSED`, `NETEVENT_TIMEOUT`, `NETEVENT_CAPSFAIL`, `NETEVENT_DONE`, and `NETEVENT_PKT_WRITTEN`. It also defines slow-accept timing/log throttling constants and a DoQ CID storage limit.

`struct comm_reply` carries the reply comm point, remote peer address, optional ancillary source-interface data, DNSCrypt state, maximum UDP size, PROXYv2-derived client address state, and, when DoQ is enabled, the DoQ ifindex, destination CID, stream ID, and source port needed to route replies back to the correct QUIC stream.

`struct comm_point` is the central transport state object. It stores event internals, socket metadata, fd, timeout, buffer ownership, TCP read/write counters, parent/free-list relationships, SSL handshake state, HTTP/1.1 parser state, HTTP/2 session and stream limits, optional DoQ socket state, DNSTAP environment, comm point type, PROXYv2 preface state, connection-close behavior flags, simultaneous read/write buffers, retry flags for draining more TCP work, TCP timeout/keepalive/connect-limit fields, optional TCP request multiplexing, optional TCP Fast Open state, optional DNSCrypt buffers, callback function, and callback argument.

The header exposes constructors for UDP, UDP with ancillary data, DoQ, TCP listeners, outgoing TCP, outgoing HTTP, local AF_UNIX descriptors, and raw descriptors. It exposes lifecycle and event-control helpers for close/delete, send/drop reply, direct UDP send, stop/start listening, change read/write interest, adjusted TCP timeouts, and memory accounting.

Timer and signal APIs expose lightweight event wrappers: create, set, disable, delete, query, bind, and callback entry points. Several internal callback functions are deliberately declared for checks and tests, including UDP, ancillary UDP, DoQ, TCP accept, TCP handler, HTTP handler, local/raw handlers, timer, signal, and slow-accept callbacks.

The HTTP/2 declarations define per-connection `http2_session`, `http_status`, and per-stream `http2_stream` state. Streams track method, content validation, content length, response status, endpoint validity, oversized-query status, independent query/response buffers, and mesh state cleanup hooks. nghttp2 callbacks and stream list helpers are declared under `HAVE_NGHTTP2`.

The DoQ declarations define compact IPv4/IPv6 socket address storage, `doq_server_socket` state, packet address metadata, packet initialization, packet sending, and timer callback entry points. The server socket stores shared connection table access, random state, address-validation settings, server CID length, idle timeout, static secret, QUIC SSL context, packet buffers, blocked packet retry state, timer marker, cached time pointers, and config.

Platform and feature-specific declarations include Winsock BIO callback wiring, TCP-connect errno logging policy, and SSL handshake log-squelch checks.
