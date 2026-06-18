
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.cc

## Purpose

`XrdHttpProtocol.cc` implements the connection-level HTTP/HTTPS protocol adapter for XRootD. It detects HTTP or TLS clients, owns the socket buffer and TLS session, parses the configuration file, authenticates clients, logs into the XRootD bridge, delegates logical HTTP/WebDAV work to `XrdHttpReq`, sends HTTP responses, loads plugins, and provides helper bridge operations such as stat and checksum queries.

## Important APIs, Types, And Functions

- Static configuration and runtime globals include TLS paths/options, redirect/listing/static-resource settings, token `secretkey`, gridmap/secxtractor state, external handlers, CORS handler, checksum handler, read-range config, static response headers, packet marking handle, and protocol object pool `ProtStack`.
- `XrdHttpProtocol(bool imhttps)`, `Reset()`, `Cleanup()`, and `Recycle()` manage object reuse, buffer ownership, SSL shutdown, `SecEntity` memory, and bridge/request state.
- `Match(XrdLink*)` peeks the connection to decide HTTP versus HTTPS, obtains/reuses a protocol instance, marks the link dialect as HTTPS for the framework, allocates a 1 MiB buffer, and binds the link.
- `Process(XrdLink*)` is the main state machine. It performs TLS handshake, token authentication for plain HTTP redirects, bridge login, header parsing, self-redirect, user-agent monitor info setting, and finally `CurrentReq.ProcessHTTPReq()`.
- Buffer helpers `BuffgetLine()`, `getDataOneShot()`, `BuffAvailable()`, `BuffUsed()`, `BuffConsume()`, and `BuffgetData()` implement a circular read buffer over `XrdLink` or OpenSSL.
- Response helpers `SendData()`, `StartSimpleResp()`, `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, `ChunkRespHeader()`, and `ChunkRespFooter()` format HTTP/1.1 responses, apply static and CORS headers, integrate monitoring, and write through TLS or raw link.
- `Configure()` and `Config()` wire XRootD environment services, monitoring, checksums, OpenSSL BIOs, TLS context selection, plugin loading, CORS, header-to-CGI mappings, static headers, role detection, and object-pool cleanup.
- Directive parsers include TLS (`xhttpsmode`, `xsslcert`, `xsslkey`, `xsslcadir`, `xsslcafile`, `xsslverifydepth`, `xsslcipherfilter`, `xtlsreuse`, `xtlsclientauth`), auth/security (`xsecretkey`, `xgmap`, `xsecxtractor`, `xauth`), behavior (`xlistdeny`, `xlisting`, `xlistredir`, `xdesthttps`, `xselfhttps2http`, `xmaxdelay`), static content (`xembeddedstatic`, `xstaticredir`, `xstaticpreload`, `xstaticheader`), CORS/external handlers, tracing, and `xheader2cgi`.
- Plugin loaders `LoadSecXtractor()`, `LoadExtHandlerNoTls()`, `LoadExtHandler()`, `LoadCorsHandler()`, `ExtHandlerLoaded()`, and `FindMatchingExtHandler()` support dynamic extension points.
- `doStat()` and `doChksum()` construct bridge requests for `kXR_stat` and `kXR_query/kXR_Qcksum`.

## Control Flow

Connection dispatch begins in `Match()`, which classifies printable data as HTTP and non-printable TLS-like data as HTTPS only when HTTPS is configured. The selected protocol object is bound to the link and later processed by `Process()`.

`Process()` first initializes request timing for monitoring and ensures a client host is present in `SecEntity`. HTTPS connections run a nonblocking `SSL_accept()` flow, optional `secxtractor` SSL initialization, client auth through `HandleAuthentication()`, and then set `ssldone`. Plain HTTP with an opaque `xrdhttptk` validates redirect tokens and reconstructs security fields from signed CGI parameters; plain HTTP without a valid token is rejected when `secretkey` is configured.

After authentication, if no external handler matches, the protocol logs into `XrdXrootd::Bridge` using the derived `SecEntity`. Bridge login is asynchronous: `DoingLogin` and `DoneSetInfo` coordinate callbacks and optional `monitor info <user-agent>` submission through a `kXR_set` bridge request. Once logged in, buffered header lines are parsed into `CurrentReq`; incomplete headers return `1` to await more data, while malformed headers send `400` and close. A configured `selfhttps2http` path redirects suitable HTTPS requests to this same endpoint over HTTP with signed opaque credentials. Finally `CurrentReq.ProcessHTTPReq()` performs method-specific work.

Config flow starts in `Configure()`, records scheduler/buffer/logger/env handles, then calls `Config()`. `Config()` imports `XRD_READV_LIMITS`, initializes monitoring and optional thread, sets up checksum handling, constructs OpenSSL BIO callbacks, parses `http.*` directives, computes static header strings, loads CORS, resolves HTTPS auto/manual/disabled modes, initializes TLS if needed, loads external handlers, and initializes security.

## State And Persistence

Most settings are static process-global configuration. Per-connection state includes `Link`, `myBuff`, circular buffer pointers, `SecEntity`, TLS objects, `Bridge`, and `CurrentReq`. `Reset()` prepares an object for reuse but does not free all static configuration. `Cleanup()` returns buffers and frees TLS/security strings for the current connection. There is no persistent storage except configured files read at startup, preloaded static files stored in memory, and MonRoll/GStream process metrics.

## Dependencies And Integration Points

This file is tightly integrated with the XRootD core: `XrdProtocol`, `XrdLink`, `XrdBuffer`, `XrdBuffManager`, `XrdScheduler`, `XrdXrootd::Bridge`, `ClientRequest`, TLS (`XrdTlsContext`, OpenSSL `SSL/BIO`), security (`XrdSecEntity`, gridmap, secxtractor), tracing, packet marking, checksum handler, CORS plugin, external HTTP handlers, and monitoring. `XrdHttpReq` is a friend and directly accesses protocol internals such as `Bridge`, `Link`, response helpers, static settings, CORS, and buffer methods.

## Risks And Edge Cases

- Protocol detection is intentionally loose: printable bytes are accepted as HTTP, and TLS detection depends on `httpsmode`.
- `Match()` unconditionally marks the link address dialect as HTTPS/TLS after match, even before plain HTTP handling; this is a framework workaround and may surprise other integrations.
- The circular buffer code uses pointer arithmetic and aborts on invariant violations. Off-by-one mistakes or oversized headers can terminate the process.
- TLS handshake temporarily sets socket timeouts and relies on custom BIO callbacks; failures must not leak `ssl` or leave stale `sbio`.
- `xsecretkey()` permission check uses bitwise chaining in a way that may not express the intended "world readable or group writable" policy clearly.
- Static global config is mutable during startup and not protected by locks; runtime reconfiguration would be unsafe.
- `StartSimpleResp()` accepts arbitrary `header_to_add`; callers must ensure CRLF-safe content.
- Static preload reads up to 64 KiB but can leak allocated `StaticPreloadInfo` on failure after allocation.
- External handlers and secxtractor are dynamically loaded and trusted; matching happens before bridge login for paths they own.
- Monitoring finalization depends on response helper call order. `SendData()` failures set `ERR_NET`; callers must call monitoring again to record the error.

## Test Signals

High-value tests include HTTP/HTTPS protocol match, TLS disabled behavior, token-auth success/failure and expiry, self-redirect URL construction for IPv4/IPv6, header parsing with partial circular-buffer wrap, malformed and oversized headers, response header generation with static headers and CORS, chunked final/trailer monitoring paths, config parser directives including invalid inputs, external handler matching and no-TLS loading, `header2cgi` strip-on-redirect behavior, checksum query construction, and cleanup/recycle memory ownership. Integration tests should exercise bridge login callbacks, `DoingLogin` user-agent `kXR_set`, and keepalive versus close return codes.
