# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMan.hh

## Purpose
Declares `XrdCmsClientMan`, the object representing one remote CMS manager connection from a client/redirector perspective.

## Important APIs, Types, and Functions
Public API includes `delayResp`, `isActive`, `nextManager`, `Name`, `NPfx`, `manPort`, `Send()` overloads, `Start`, `Suspended`, `setNext`, `setNetwork`, `setConfig`, `whatsUp`, and `waitTime`. Private helpers handle hookup, receive, async response relay, status check, and status set.

## Control Flow
Higher-level CMS clients create one object per manager, run `Start()` in a thread, send requests through `Send()`, and query active/suspended state while manager replies are matched through `XrdCmsClientMsg` and `XrdCmsRespQ`.

## State and Persistence Behavior
State includes static network/config/buffer-pool data, linked-list pointer, connection link, host strings, port, instance/mask values, counters, timing fields, response header, and reusable network buffer. State is process-local and manually owned.

## Dependencies and Integration Points
Includes YProtocol headers, CMS response queues, Ouc buffer/error info, atomics, and pthread wrappers. Forward-declares `XrdInet` and `XrdLink`.

## Risks and Edge Cases
Inline atomic macros hide locking behavior and should be kept consistent with implementation locks. Manual memory ownership of `Host`, `HPfx`, `NetBuff`, and `Link` requires destructor coverage. Static network pointer must be set before connection threads start.

## Test Signals
Compile tests should catch protocol header changes. Unit tests should cover constructor defaults, linked manager chaining, static network/config setup, and suspended/active accessors under lock.
