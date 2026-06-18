# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.cc

## Purpose
`XrdNetSecurity.cc` implements host/netgroup authorization for network endpoints. It supports exact IP caching, hostname pattern matching, and system netgroups.

## Important APIs, Types, and Functions
`AddHost()` adds exact resolvable hosts directly into the OK IP hash or stores wildcard/pattern hosts in `HostList`. `AddNetGroup()` records allowed netgroups. `Authorize()` resolves a string or evaluates an `XrdNetAddr`. `Merge()` combines another security object and deletes it. Private `addHIP()` resolves host IPs, while `hostOK()` caches and unlocks successful authorization.

## Control Flow
Authorization formats the address as normalized IP text, checks the OK cache under `okHMutex`, resolves a hostname if netgroups or host patterns are configured, checks netgroups with `innetgr()`, then checks the host pattern list. Successful checks add the IP to the OK cache and unlock through `hostOK()`. Failure unlocks and returns false.

## State and Persistence
State is in-memory per `XrdNetSecurity`: pattern list, netgroup linked list, OK IP hash cache, mutex, trace pointer, and booleans indicating whether pattern/netgroup checks are needed. No disk persistence.

## Dependencies and Integration Points
It depends on `XrdNetAddr`, `XrdNetUtils::GetAddrs()`, `XrdOucHash`, `XrdOucNList`, pthread locks, and platform `innetgr()` support. Core `Xrd`, CMS, and PSS configuration create and use these objects for peer authorization.

## Risks and Test Signals
Risks include lock discipline because `hostOK()` unlocks on behalf of callers, platform stubs where `innetgr()` always denies on MUSL/Windows, stale DNS-to-IP cache, and pattern resolution behavior for `+`. Tests should cover exact hosts, wildcard hosts, expanded hosts, netgroups, cache hits, merge duplicate netgroups, unknown host denial, and platform-specific netgroup stubs.
