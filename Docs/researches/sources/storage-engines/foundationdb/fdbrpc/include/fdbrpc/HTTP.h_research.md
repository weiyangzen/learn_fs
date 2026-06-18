# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/HTTP.h

## Purpose
`HTTP.h` declares lightweight HTTP request/response parsing, writing, client request execution, proxy CONNECT support, and simulation HTTP server registration primitives used by fdbrpc components such as blob storage integrations.

## Important APIs, Types, and Functions
The namespace defines status code constants, verb constants, case-insensitive `Headers`, URL/URI encoding helpers, MD5 helpers, `HTTPData<T>`, request/response base templates, `IncomingRequest`, `OutgoingRequest`, `IncomingResponse`, `OutgoingResponse`, `doRequest`, `proxyConnect`, `registerAlwaysFailHTTPHandler`, `IRequestHandler`, `SimRegisteredHandlerContext`, and `SimServerContext`.

## Control Flow
Incoming request/response types read from an `IConnection`; outgoing responses write to one. `doRequest` sends an outgoing request to a connection under optional send/receive rate controls and parses the incoming response. `proxyConnect` establishes a tunnel through an HTTP proxy. Simulation server contexts register handlers, bind listeners, and route incoming requests to cloned request handlers.

## State and Persistence Behavior
HTTP data is per request/response. Simulation server contexts store handler registration, DNS addresses, listener futures, actor collections, and running state. There is no durable persistence.

## Dependencies and Integration Points
It depends on Flow networking, `IConnection`, rate control, packet queues, actor collections, and network addresses. It integrates with simulated HTTP servers, blob-store clients, and proxy-aware outbound connections.

## Risks and Edge Cases
Header handling is case-insensitive but still string-based. Content length and MD5 validation depend on implementation in the corresponding source. Handler cloning must avoid sharing per-instance mutable state, as documented. `isHeaderOnlyResponse` treats DELETE and CONNECT as header-only, which must match caller expectations.

## Test Signals
Signals include HTTP parser/writer tests, blob-store request tests, proxy CONNECT tests, MD5 verification behavior, and simulation handlers receiving expected requests.
