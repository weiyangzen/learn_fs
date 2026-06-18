# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.hh

## Purpose
`XrdNetRefresh.hh` declares `XrdNetRefresh`, an `XrdJob` used to periodically refresh connected UDP destination addresses.

## Important APIs, Types, and Functions
`DoIt()` overrides the scheduler job callback. Static `Register()` and `UnRegister()` manage refreshable peer FDs. Static `Start()` initializes the singleton job. Private helpers validate registration failures, replace destinations, and run updates.

## Control Flow and State
The header presents the class as a singleton-style service with only static management methods plus a scheduler job instance. The constructor names the job `"NetRefresh"`.

## Dependencies and Integration Points
It forward-declares peer, scheduler, and error classes and inherits from `XrdJob`. It is started by core configuration and used by UDP message code.

## Risks and Test Signals
The API assumes callers register only connected UDP sockets and unregister before FD reuse. Tests should verify registration validation and scheduler invocation through `DoIt()`.
