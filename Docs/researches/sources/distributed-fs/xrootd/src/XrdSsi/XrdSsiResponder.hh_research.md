# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResponder.hh

## Purpose
`XrdSsiResponder.hh` declares the protected server-side response helper used by SSI service task objects to bind to an `XrdSsiRequest`, read request input, post alerts, and send exactly one final response. It is deliberately a companion/friend of `XrdSsiRequest`, hiding the request internals behind a responder API while preserving strict ownership and lifetime rules.

## Important APIs and Types
The public binding API is `BindRequest(XrdSsiRequest&)` and `UnBindRequest()`. Protected response methods include `Alert`, `GetRequest`, `ReleaseRequestBuffer`, `SetMetadata`, `SetErrResponse`, `SetNilResponse`, `SetResponse(const char *, int)`, `SetResponse(long long, int)`, and `SetResponse(XrdSsiStream *)`. The abstract `Finished(XrdSsiRequest&, const XrdSsiRespInfo&, bool cancel)` callback is the required cleanup hook for derived responders. `Status` reports `wasPosted`, `notPosted`, or `notActive`. `MaxMetaDataSZ` and `MaxDirectXfr` both cap direct metadata/data transfer at 2 MiB.

## Control Flow
A service-created responder first calls `BindRequest`, then may inspect request data or set metadata, and finally posts one response. The implementation in `XrdSsiResponder.cc` validates that a request is still bound, locks the responder mutex before the request mutex, fills `XrdSsiRespInfo`, and calls `XrdSsiRequest::ProcessResponse`. When the request finishes or is canceled, `XrdSsiRequest::Finished` invokes the derived `Finished` method; only after that should the responder call `UnBindRequest`.

## State and Persistence
The class persists no disk state. Its in-memory state is `spMutex`, `reqP`, and reserved ABI fields. The comments document that response buffers, metadata buffers, and stream objects must remain valid until `Finished` runs, so derived responders own these resources until the framework hands them back.

## Dependencies and Integration Points
It depends on `XrdSsiRequest.hh`, `XrdSsiStream`, `XrdSsiRespInfo`, `XrdSsiRespInfoMsg`, and SSI mutex semantics. Friend access is granted to `XrdSsiRequest` and `XrdSsiRRAgent`. `XrdSsiTaskReal` derives from this responder path to translate endpoint responses into SSI responses.

## Risks and Test Signals
The main risks are response-after-finish races, posting multiple responses, deleting a responder before unbinding, and buffers that are freed before `Finished`. Tests should exercise normal bind/respond/finish/unbind, cancellation, responder destruction while bound, metadata length bounds, direct transfer limit behavior, nil/error/file/stream responses, and alert recycling when no request is bound.
