# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.cc

## Purpose

This file implements the XRootD client transport handler. It owns message framing over nonblocking sockets, XRoot protocol handshake/login/authentication/bind state machines, TLS/protection decisions, request marshalling and response unmarshalling, multiplexing over substreams, connection idleness/brokenness checks, request signing, stream disconnect cleanup, and request-description logging.

It is the main protocol glue between `PostMaster`/socket infrastructure and XRoot protocol structs from `XProtocol.hh`.

## Important APIs, types, and functions

- `PluginUnloadHandler` registers an `atexit` callback for `root`/`xroot` transport handlers and uses an RW lock plus `unloaded` flag to prevent security plugin use during unload.
- `XRootDStreamInfo` tracks each substream status (`Disconnected`, `Broken`, `HandShakeSent`, `HandShakeReceived`, `LoginSent`, `AuthSent`, `BindSent`, `EndSessionSent`, `Connected`), protocol path id, and per-stream server flags.
- `StreamSelector` tracks outstanding response counts per data substream and selects the least-loaded connected stream for reads/page reads/readv responses.
- `BindPrefSelector` cycles through server-advertised bind-preference URLs.
- `XRootDChannelInfo` is the per-channel state block stored in `AnyObject`: server flags, protocol version, current/old session ids, SID manager, authentication/protection objects, stream vector, sent-open/close SID tracking, file-instance/open-file counters, wait barrier, TLS/TPC flags, bind selector, login token, and mutex.
- `GetHeader()`, `GetBody()`, and `GetMore()` implement nonblocking response reads. They allocate/reallocate `Message` buffers, preserve cursor progress across `suRetry`, unmarshal headers and status-more bodies, and validate `kXR_status` sizes.
- `InitializeChannel()` creates `XRootDChannelInfo`, sizes substreams from `SubStreamsPerChannel`, initializes the stream selector, and derives secure/TPC/login-token flags from the URL.
- `HandShake()`, `HandShakeMain()`, `HandShakeParallel()`, and `HandShakeDone()` implement the connection state machines.
- `IsStreamTTLElapsed()` and `IsStreamBroken()` use env-configured TTL/timeout settings, open-file/file-instance counts, allocated/old SIDs, and wait barriers to decide whether streams can be disconnected or are likely broken.
- `MultiplexSubStream()` rewrites read-like requests to carry a selected response path id, then returns `(up, down)` `PathID`.
- `SubStreamNumber()` decides how many substreams to create, including TLS-control/plain-data cases that require at least a second stream.
- `MarshallRequest()`, `UnMarshallRequest()`, `UnMarshallBody()`, `UnMarshalStatusBody()`, `UnMarchalStatusMore()`, and `UnMarshallHeader()` do endian conversion and integrity checks for XRoot protocol structures.
- `MessageReceived()` updates substream load counters, wait barriers, timed-out SID handling, and open/close counters. It can request a close for an open response that arrived after the request timed out.
- `MessageSent()` records open/close SIDs so later responses can update counters.
- `GetSignature()` signs/protects requests through `XrdSecProtect` when the negotiated protection policy requires it.
- `NeedEncryption()` decides when TLS must be enabled based on user URL, `NoTlsOK`, stream status, and server flags such as `kXR_gotoTLS`, `kXR_tlsLogin`, `kXR_tlsSess`, and `kXR_tlsData`.
- Private generation/processing helpers build and parse handshake, protocol, bind, login, auth, and end-session messages.
- `GenerateDescription()` and `FileHandleToStr()` produce log descriptions for many request types.

## Control flow

Incoming messages are read in two or three phases. `GetHeader()` reads exactly eight bytes, unmarshals `status` and `dlen`, and reports `suDone`. `GetBody()` reads the advertised response body. For `kXR_status` page-operation responses, `GetMore()` accounts for the nested body length, reads the correction/data segment, and calls `UnMarchalStatusMore()` to validate CRC32C and endian-convert fields.

The main stream handshake starts from `Disconnected`/`Broken`, sends initial handshake plus `kXR_protocol`, processes server handshake, processes protocol response, sends `kXR_login`, handles login, optionally performs one or more auth exchanges, optionally sends `kXR_endsess` for a previous session, and finally marks stream 0 `Connected`. Protocol negotiation may return `suRetry` when `WantTlsOnNoPgrw` causes a second protocol request with TLS enabled.

Parallel data streams follow a shorter state machine: send initial handshake/protocol expecting bind, process handshake, process protocol, send `kXR_bind`, then store the server-assigned path id and become `Connected`.

Request multiplexing is conservative. All requests use upstream stream 0 by default. For `kXR_read`, `kXR_pgread`, and `kXR_readv`, the transport chooses a connected data stream for the response path and rewrites the request body/path id before remarshal. Writes, writev, and pgwrite have path-id code intentionally disabled because server-side write multiplexing is noted as not working properly.

Authentication starts after login advertises security data. The transport creates `XrdOucEnv` with socket/user/password and `xrd.`/`xrdcl.` URL parameters, creates `XrdSecParameters`, loads the security factory, iterates protocols until one returns credentials, sends `kXR_auth`, handles `kXR_authmore`, falls back to another protocol on server auth error, and installs `XrdSecProtect` if the protocol response advertised protection requirements.

TLS is negotiated as a state-dependent side effect. `InitProtocolReq()` advertises TLS ability/want flags based on user settings and `InitTLS()`. `NeedEncryption()` is called by the stream layer around handshake transitions to switch TLS before login, before bind, after login/session, or immediately on `gotoTLS`.

## State and persistence behavior

All transport state is per-channel in `XRootDChannelInfo` and guarded by `info->mutex` for most operations. Important mutable state includes:

- `stream` vector status/path ids/server flags per substream.
- Current and old 16-byte session ids, needed for reconnect/end-session cleanup.
- `sidManager` state owned by a shared manager pool keyed by URL channel id.
- `sentOpens` and `sentCloses` sets that map request SIDs to pending open/close accounting.
- `openFiles`, atomic `finstcnt`, and `waitBarrier`, which influence idle/broken stream decisions.
- Authentication objects (`authProtocol`, `authParams`, `authEnv`) and negotiated protection (`protection`, `protRespBody`, `protRespSize`).
- `encrypted`, `istpc`, bind preferences, stream name, auth protocol name, and login token.

There is no on-disk persistence. External process-global state includes the static security factory pointer in `GetAuthHandler()`, the `atexit` unload registration, environment settings read from `DefaultEnv`, and TLS/OpenSSL error queues cleared around auth.

## Dependencies and integration points

The implementation integrates with `XrdCl` socket/message/postmaster abstractions, `SIDManager`, `TransportManager`, `Tls`, `DefaultEnv`, logging, URL/env utilities, `XProtocol` wire structs/constants, `XrdNet` address utilities, `XrdOuc` CRC/token/env/error helpers, `XrdSec` authentication/protection plugins, `XrdSys` locks/timers/atomics/platform utilities, and the build version macro.

Upper layers call this through the `TransportHandler` interface declared in `XrdClXRootDTransport.hh`. Lower layers supply `Socket`, `Message`, and `HandShakeData`. Security plugins are loaded dynamically through `XrdSecLoadSecFactory()` and request protection through `XrdSecGetProtection()`.

## Risks and edge cases

- Wire-structure marshalling is broad and manual. Missing a new request type or using the wrong offset/length will produce protocol-incompatible messages.
- `UnMarshallRequest()` relies on symmetric marshalling and explicitly calls this ugly; any non-symmetric conversion change can break request rewriting.
- Several error-message paths allocate `new char[rsp->hdr.dlen-3]` and assume `dlen >= 4`; earlier unmarshalling checks cover some response classes but log paths still depend on valid server lengths.
- `MessageReceived()` dereferences `info` without a null check, unlike many other methods. A missing channel data object would crash.
- `Disconnect()` indexes `info->stream[subStreamId]` when the vector is not empty but does not bounds-check `subStreamId`.
- `DecFileInstCnt()` does not null-check `info` and does an unsynchronized load/subtract; it avoids underflow only by checking a relaxed load before `fetch_sub`.
- Authentication and protection lifetime is complex. `CleanUpProtection()` can call `CleanUpAuthentication()` only when `protection` exists, while plugin unload blocks operations through an RW lock and `unloaded` flag.
- TLS policy depends on multiple environment flags (`NoTlsOK`, `TlsNoData`, `WantTlsOnNoPgrw`) plus server protocol flags. Regression tests need matrix coverage.
- `GenerateEndSession()` combines signature and request buffers by grabbing memory from another `Message`; this depends on `Message::Grab()` semantics and can leak or alias incorrectly if those semantics change.
- `ProcessProtocolBody()` trusts protocol body tags and lengths after minimal checks; malformed bind/security requirement blocks are a security-sensitive parser surface.

## Test signals

Strong tests should include nonblocking partial header/body reads, invalid short response bodies, `kXR_status` CRC/request-id/stream-id mismatch detection, endian round-trips for every marshalled request type, handshake state transitions for main and data streams, protocol retry for TLS enforcement, auth-more/auth-failure protocol fallback, bind path-id assignment, open/close counter updates including `waitresp`, timed-out open response cleanup, stream TTL/broken decisions, request protection/signature generation, and request-description logging. Integration tests need real or mocked XRoot servers covering manager vs data server flags, TLS-required variants, and substream multiplexed reads.
