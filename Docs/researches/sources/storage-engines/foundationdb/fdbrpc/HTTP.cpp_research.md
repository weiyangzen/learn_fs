# sources/storage-engines/foundationdb/fdbrpc/HTTP.cpp

`HTTP.cpp` provides a small asynchronous HTTP/1.1 utility layer for FoundationDB REST-style clients, proxy CONNECT, and simulation HTTP services.

Key APIs include URI helpers `awsV4URIEncode`, `urlEncode`, `urlDecode`; response reason mapping in `ResponseBase<T>::getCodeDescription()`; `computeMD5Sum()` and `verifyMD5()`; header/request/response writers; read helpers for bytes, CRLF-delimited strings, fixed lengths, and headers; `readHTTPData()`; `IncomingRequest::read`; `OutgoingResponse::write/reset`; `IncomingResponse::read`; `doRequest`; `sendProxyConnectRequest`; and `proxyConnect`.

Writers prepend HTTP headers to an `UnsentPacketQueue` and drain it through `IConnection::write()` with simulated partial-write coverage. Readers accumulate bytes in strings, parse start lines and simple `Name: Value` headers, then read either `Content-Length` bodies or chunked transfer encoding. `doRequestActor()` begins response reading before request-body sending completes, allowing early server responses to close the connection. It injects optional request IDs, rate-limits send operations, validates response IDs, logs verbose details, and returns an `IncomingResponse`. Proxy CONNECT retries retryable errors/statuses with exponential backoff and honors `Retry-After`.

State is per request/response, read buffer, and packet queue; no persistence is performed. The request queue is consumed by sends. Dependencies include `fdbrpc/HTTP.h`, `IConnection`, Flow actors, `Net2Packet`, knobs, simulator buggify, `IRateControl`, MD5, and libb64.

Risks include narrow HTTP parsing, no multiline header support, simple status/request parsing, strict fixed-length trailing-byte rejection, in-place chunk decoding, optional MD5 skipping for partial content, and character-class assumptions in URI encoders. Test signals come from `HTTPServer.cpp` success/error/bad-MD5 tests plus TraceEvents for malformed headers, content mismatch, MD5 mismatch, request-ID mismatch, and proxy retries.
