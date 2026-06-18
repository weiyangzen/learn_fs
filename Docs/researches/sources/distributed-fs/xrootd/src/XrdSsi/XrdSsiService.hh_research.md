# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.hh

## Purpose
`XrdSsiService.hh` defines the abstract Scalable Service Interface service contract. It is used both client-side, where many service instances may exist, and server-side, where one provider-supplied service processes all requests.

## Important APIs and Types
`SsiVersion` is the ABI/version gate. `GetVersion` returns that version. `Attach` is a virtual hook for foreground reattachment to backgrounded requests. `Prepare` is an optional preflight hook for resource authorization, redirect, or stall behavior. `ProcessRequest` is pure virtual and returns all results via the request callbacks. `Stop` is a client-side lifecycle hook with immediate or deferred semantics.

## Control Flow
Server-side SSI can call `Prepare` before subsequent requests and `ProcessRequest` to execute work. `Attach` receives the original server request and optional resource description, allowing services to reject attach attempts when the attaching client should not inherit the original detached work.

## State and Persistence
The base class stores no data. Derived classes own all request, session, and service state. The protected destructor enforces lifecycle through `Stop` rather than direct deletion.

## Dependencies and Integration Points
The contract references `XrdSsiErrInfo`, `XrdSsiRequest`, and `XrdSsiResource`. Providers return service objects through `XrdSsiProvider::GetService`; client and server plugin entry points must agree on `SsiVersion`.

## Risks and Test Signals
ABI mismatch is a key integration risk. Tests should verify version checking, default `Attach` acceptance, default `Stop` return values, and service-specific `Prepare` handling for EAGAIN redirect, EBUSY stall, and authorization failures.
