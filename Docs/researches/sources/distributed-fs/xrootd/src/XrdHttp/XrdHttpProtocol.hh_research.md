
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpProtocol.hh

## Purpose

`XrdHttpProtocol.hh` declares the XRootD protocol plugin class that presents HTTP/WebDAV over the XRootD framework. It defines the connection adapter, configuration surface, bridge integration, buffer utilities, TLS/security state, response helpers, plugin registries, static resource settings, monitoring-adjacent dependencies, and friend access needed by `XrdHttpReq` and external request wrappers.

## Important APIs, Types, And Functions

- `class XrdHttpProtocol : public XrdProtocol` is the protocol object managed by `XrdObjectQ`.
- Public lifecycle and framework hooks: `Configure()`, `Match()`, `Process()`, `Recycle()`, `Stats()`, `DoIt()`, constructor/destructor, copy constructor, and assignment operator.
- Public helper operations: `doStat()`, `doChksum()`, `parseHeader2CGI()`, `isHTTPS()`.
- Public/static shared objects: `ProtStack`, `ProtLink`, `SecEntity`, `cksumHandler`, and `ReadRangeConfig`.
- Private response API used by `XrdHttpReq`: `StartSimpleResp()`, `SendSimpleResp()`, `StartChunkedResp()`, `ChunkResp()`, `ChunkRespHeader()`, `ChunkRespFooter()`, and `SendData()`.
- Private connection helpers: `CreateBIO()`, `getDataOneShot()`, `BuffgetLine()`, `BuffgetData()`, `BuffConsume()`, `BuffAvailable()`, `BuffUsed()`, `BuffFree()`, `GetClientIPStr()`, `Cleanup()`, and `Reset()`.
- Configuration parsers and loaders cover TLS, security extractors, CORS, external handlers, listings, static assets, header-to-CGI rules, trace, auth, and delay limits.
- `extHInfo` temporarily stores external handler load requests until enough config/environment context exists.
- `XrdHttpExtHandlerInfo` stores up to four loaded external handler instances by short name.
- Static configuration fields model role, TLS, redirects, static content, checksum list, packet marking, credential forwarding, and static response headers.

## Control Flow

The header shapes a two-level state machine. The XRootD framework calls `Match()` to claim a link, then `Process()` repeatedly as socket or bridge events arrive. `Process()` uses buffer methods and TLS helpers, then lets `CurrentReq` drive HTTP method work through bridge callbacks. `DoIt()` invokes `Resume` if set, but this code path is mostly dormant in the observed implementation.

Configuration functions are static because they apply to the protocol plugin rather than an individual connection. Loaded plugins and TLS context are shared by all instances. `friend class XrdHttpReq` and `friend class XrdHttpExtReq` intentionally expose protocol internals so request handlers can issue bridge commands and send responses without a large public API.

## State And Persistence

Per-instance mutable state includes the link, client address string, current request, bridge pointer, socket buffer, TLS session/BIO, security entity, login flags, resume fields, and HTTPS flags. Static state includes all configuration and plugin pointers. The object pool `ProtStack` reuses instances; destructor and recycle paths call `Cleanup()`/`Reset()`. There is no durable persistence defined by the header.

## Dependencies And Integration Points

This header pulls in many framework interfaces: `XrdProtocol`, `XrdObject`, `XrdSysError/Pthread`, `XrdSecInterface`, `XrdXrootdBridge`, `XrdOucStream/Hash`, `XrdHttpChecksumHandler`, `XrdHttpReadRangeHandler`, `XrdNetPMark`, `XrdHttpCors`, and `XrdHttpReq`. It also depends on OpenSSL and standard containers. Its primary local consumers are `XrdHttpProtocol.cc` and `XrdHttpReq.cc`.

## Risks And Edge Cases

- Friend-based coupling makes `XrdHttpReq` sensitive to private field changes.
- Static configuration fields mean tests and embedded uses must isolate global state carefully.
- `MAX_XRDHTTPEXTHANDLERS` is fixed at four and handler names are limited to 15 stored characters plus terminator.
- Raw pointers and manual ownership dominate TLS paths, security strings, buffers, preloaded static data, and plugins.
- `operator=` returns by value and is effectively a no-op; accidental use would be surprising.
- The response helper overloads have similar names but different semantics; misuse can skip monitoring or produce malformed headers.

## Test Signals

Compile and API tests should detect changes to friend-required private methods, handler limits, and static field declarations. Functional tests should instantiate protocol objects with fake `XrdLink`/buffer manager services, exercise recycle/reset behavior, and verify response helpers through `XrdHttpReq` because the intended API is friend-mediated.
