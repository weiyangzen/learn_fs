# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpConnectionCallout.hh

## Purpose
`XrdClHttpConnectionCallout.hh` declares the public extension point that lets clients provide a custom socket acquisition path for HTTP requests, for example through a broker or out-of-band connection service.

## Important APIs and Types
`ConnectionCallout` is an abstract class with `BeginCallout` and `FinishCallout`. `BeginCallout` returns a listener FD and expiration time or `-1` with an error string. `FinishCallout` is invoked when the listener FD is readable and returns the connected socket FD or `-1`. `CreateConnCalloutType` is a C-linkage-compatible function pointer taking URL and `ResponseInfo` and returning an owned `ConnectionCallout *`.

## Control Flow
Users set the `XrdClConnectionCallout` property on a `File` or `FileSystem` to a serialized hex function pointer. Operations parse that pointer, call the creator with URL/response info, register the returned listener FD with the worker loop, and later finish the callout when ready.

## State and Persistence
The callout object is owned by the HTTP operation once created. It may outlive the initiating call until timeout or socket readiness. No repository or disk state is persisted.

## Dependencies and Integration Points
The interface uses `std::chrono`, strings, and `ResponseInfo`. Implementations are external to this plugin but integrate through `CurlOperation` socket callbacks and worker polling.

## Risks and Test Signals
Serializing function pointers through strings is inherently unsafe across ABI boundaries and must be tightly controlled by callers. Tests should cover malformed pointer properties, callout timeout, failed begin/finish, FD lifetime, and fallback to libcurl default connection behavior when the creator returns null.
