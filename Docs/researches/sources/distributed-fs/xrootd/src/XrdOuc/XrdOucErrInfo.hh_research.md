# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucErrInfo.hh

## Purpose
Defines the central error, data, user-capability, environment, and callback carrier used between XRootD plugins and framework components.

## Important APIs, Types, And Functions
`XrdOucEI` contains fixed 2048-byte message storage, user pointer, capability flags, and code. Capability constants advertise async replies, redirects, IPv4/IPv6 support, private-network status, file URL support, redirect flags, and EC redirects. `XrdOucErrInfo` offers setters/getters for error code/text, external `XrdOucBuffer` text, user, callback object/argument, environment, trace data offset, monitoring id, and user capabilities. `XrdOucEICB` declares virtual `Done` and `Same`.

## Control Flow
Callers fill `XrdOucErrInfo` synchronously with `setErrInfo` or attach a callback/environment. Callback and environment are mutually exclusive in the API: `getEnv` returns null when callback is set, and `setEnv` clears callback state. `Reset` recycles external buffers and clears code/message. Assignment clones external buffers when present.

## State And Persistence
State is in-memory. Fixed message storage is embedded; extended data is owned as an `XrdOucBuffer*` and recycled. User string, callback object, and environment pointers are non-owned.

## Dependencies And Integration Points
Depends on `XrdOucBuffer`, `XrdSysPlatform`, and callback implementers such as `XrdOucCallBack`. It is a broad ABI surface for plugins, redirects, monitoring, and asynchronous completion.

## Risks And Test Signals
Risks include non-owned pointer lifetimes, the callback/environment union requiring disciplined use, `setErrData` offset bounds depending on caller input, fixed-buffer truncation, and lack of locking. Test signals include buffer recycling, assignment clone behavior, callback completion contract, environment handoff, capability flag propagation, and long message truncation.
