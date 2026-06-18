# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.hh

## Purpose

This header declares `XrdCl::XRootDTransport`, the concrete `TransportHandler` for XRootD protocol channels. It exposes the transport contract used by the postmaster/network layer: message reading, channel initialization, handshake progress, stream health, multiplexing, marshalling/unmarshalling helpers, message notifications, protection signatures, TLS decisions, and bind preferences.

The declarations here define which parts of the large implementation in `XrdClXRootDTransport.cc` are public/static utility surface versus private handshake/auth helpers.

## Important APIs, types, and functions

- Public lifecycle and I/O overrides: constructor/destructor, `GetHeader()`, `GetBody()`, `GetMore()`, `InitializeChannel()`, `FinalizeChannel()`, `HandShake()`, and `HandShakeDone()`.
- Stream health and routing: `IsStreamTTLElapsed()`, `IsStreamBroken()`, `Multiplex()`, `MultiplexSubStream()`, `SubStreamNumber()`, and `NeedControlConnection()` which always returns `true`.
- Wire conversion helpers: static `MarshallRequest(Message*)`, `MarshallRequest(char*)`, `UnMarshallRequest()`, `UnMarshallBody()`, `UnMarshalStatusBody()`, `UnMarchalStatusMore()`, and `UnMarshallHeader()`.
- Diagnostics and state queries: `LogErrorResponse()`, `NbConnectedStrm()`, `Disconnect()`, `Query()`, `GenerateDescription()`, and inline `SetDescription()`.
- Message event hooks: `MessageReceived()` and `MessageSent()` let the transport update stream-selection and open/close accounting.
- Security/TLS hooks: `GetSignature(Message*, Message*&, AnyObject&)`, `GetSignature(Message*, Message*&, XRootDChannelInfo*)`, `WaitBeforeExit()`, `NeedEncryption()`, and private auth/protection cleanup/loading methods.
- File/channel accounting: `DecFileInstCnt()` decrements the channel-bound file object count.
- Bind routing: `GetBindPreference()` returns server-advertised bind-preference URLs when available.
- Private handshake helpers: `HandShakeMain()`, `HandShakeParallel()`, message generators/processors for initial handshake/protocol/bind/login/auth/end-session, `ProcessProtocolBody()`, `InitProtocolReq()`, `GetCredentials()`, `GetAuthHandler()`, `ServerFlagsToStr()`, and `FileHandleToStr()`.
- `PluginUnloadHandler` is forward-declared and friended so unload coordination can access private transport state.

## Control flow

The transport handler interface is event-driven. The postmaster repeatedly calls `GetHeader()`, `GetBody()`, and for page status responses `GetMore()` as nonblocking sockets become readable. It calls `HandShake()` with `HandShakeData` until the returned status indicates done or continuation; `HandShakeDone()` gives a boolean guard for stream readiness.

Outgoing messages are prepared by upper layers and then passed through `MarshallRequest()` and optional `SetDescription()`. Before send, the postmaster can ask `Multiplex()`/`MultiplexSubStream()` for `(up, down)` path routing and can request a protection message with `GetSignature()`. After send/receive, `MessageSent()` and `MessageReceived()` feed transport bookkeeping.

The private handshake helpers split the protocol into clear phases: main control stream login/auth/session handling and parallel data-stream bind handling. The public `NeedEncryption()` hook allows the surrounding stream implementation to turn TLS on at specific points selected by private state.

## State and persistence behavior

The header itself declares only one data member: `PluginUnloadHandler *pSecUnloadHandler`. All channel-specific mutable state is hidden behind the forward-declared `XRootDChannelInfo` stored in `AnyObject`, constructed in the `.cc` file. That separation keeps the public class size small while preserving a rich per-channel state machine internally.

There is no durable persistence. `WaitBeforeExit()` coordinates process shutdown for dynamically loaded security/protection code; `NeedControlConnection()` documents that data streams depend on the control connection.

## Dependencies and integration points

The header depends on `XrdClPostMaster.hh` for `TransportHandler`, `HandShakeData`, `PathID`, and query/action contracts; `XrdClMessage.hh`; `XProtocol/XProtocol.hh`; `XrdSec/XrdSecInterface.hh`; and `XrdOuc/XrdOucEnv.hh`. It forward-declares `Tls`, `Socket`, `XRootDChannelInfo`, `PluginUnloadHandler`, `XrdSysPlugin`, and `XrdSecProtect`.

Consumers include the XRootD transport manager, message readers/writers, postmaster, file/file-system state handlers, and any code using static marshalling/unmarshalling helpers or query IDs such as `XRootDQuery::ServerFlags`.

## Risks and edge cases

- The public static wire helpers operate on raw `char*`/`Message*` buffers and require callers to know whether data is already marshalled.
- `UnMarchalStatusMore` is misspelled in the API, so downstream code must use that exact symbol.
- `NeedControlConnection()` being hardcoded `true` means any future transport variant that can run independent data streams would need a new handler or override change.
- `FinalizeChannel()` is declared but implemented as a no-op; channel state lifetime is therefore likely owned by `AnyObject`/postmaster conventions outside this class.
- Forward declarations hide important state invariants from header readers. Correct use requires following the `.cc` implementation, especially for TLS/auth/protection and stream accounting.

## Test signals

Compile-level tests should catch signature drift between this header and `XrdClXRootDTransport.cc`. Behavioral tests should exercise every `TransportHandler` override through the postmaster abstraction rather than only static helpers, plus focused unit tests for static marshalling/unmarshalling helpers. Shutdown tests should cover `WaitBeforeExit()`/security unload behavior, while integration tests should confirm `NeedControlConnection()`, substream counts, multiplexing, and bind preferences behave correctly for manager, data-server, TPC, and TLS configurations.
