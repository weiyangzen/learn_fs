# sources/distributed-fs/xrootd/src/XrdNet/XrdNetRefresh.cc

## Purpose
`XrdNetRefresh.cc` maintains connected UDP sockets whose destination hostnames may resolve to new addresses over time. It periodically re-resolves registered peers and reconnects or replaces sockets when their destination IP changes.

## Important APIs, Types, and Functions
The file defines global `XrdNetSocketCFG::NetRefresh` and `udpRefr`, private `RefInfo`, `fd2Info`, `refMTX`, and scheduler/error pointers. Public methods are `Start()`, `Register()`, `UnRegister()`, and job `DoIt()`. Private helpers are `RegFail()`, `SetDest()`, and `Update()`.

## Control Flow
`Start()` installs logger/scheduler pointers, allocates the never-deleted job object, and schedules it. `Register()` validates hostname, FD, socket-ness, and `SOCK_DGRAM`, records `hostname:port` with a monotonically increasing instance ID, and rejects duplicate FDs. `Update()` copies the registry under lock, performs DNS resolution without holding the lock, then reacquires the lock and applies still-current updates. Same-family changes use `connect()` on the original FD; family changes create a new socket, connect it, and atomically replace the original FD with `dup2`. `DoIt()` calls `Update()` and reschedules.

## State and Persistence
All state is in memory: FD-to-host mapping, instance IDs to prevent stale updates, and scheduler registration. There is no disk persistence. Registered sockets outlive the refresh service and are unregistered explicitly.

## Dependencies and Integration Points
It depends on `XrdScheduler`, `XrdNetPeer`, `XrdNetAddr`, `XrdNetUtils::Compare()`, `XrdSysFD` wrappers, and pthread mutex helpers. `XrdNetMsg` registers UDP peers, and `XrdConfig` starts the service with configured refresh intervals.

## Risks and Test Signals
There is a likely logic issue: `Update()` treats anything other than `IPDiff` as a family exception before computing `newFam`, so `IPDFam` changes cannot reach `SetDest()` even though `SetDest()` supports them. Other risks include duplicate scheduling from both `DoIt()` and `Update()`, races with FD close/reuse, DNS failures causing noisy logs, and the typo-laden diagnostics. Tests should simulate DNS changes, same-family reconnects, family changes, unregister while update is pending, duplicate FD registration, invalid hostnames, and UDP-only validation.
