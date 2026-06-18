# sources/distributed-fs/xrootd/src/XrdNet/XrdNetPMarkFF.cc

## Purpose
`XrdNetPMarkFF.cc` implements the Firefly packet-marking handle. It builds RFC5424-like syslog JSON messages for flow lifecycle start/end events, gathers TCP usage/RTT statistics, and sends messages to configured collector and/or origin UDP destinations.

## Important APIs, Types, and Functions
`Start()` initializes flow identity, UDP destinations, JSON header/tail fragments, and sends the start message. `Emit()` collects socket statistics, formats the lifecycle message, and sends through `netMsg` and/or `netOrg`. `SockStats()` uses Linux `TCP_INFO` when available. `getUTC()` formats UTC timestamps with microseconds. The destructor emits the end message and releases allocated state.

## Control Flow
`XrdNetPMarkCfg::Begin()` constructs the handle and calls `Start()`. `Start()` reads the socket FD from `XrdNetAddrInfo`, obtains peer and local addresses with `XrdNetUtils::GetSokInfo()`, prepares collector/origin routing, formats static JSON context, chooses source/destination orientation based on `http-put`, sets `fdOK`/`odOK`, and emits `"start"`. Destruction emits `"end"` only for still-valid reporting paths.

## State and Persistence
Per-flow state includes copied peer address for origin reporting, optional chained extra handle, tident, destination strings, JSON fragments, socket FD, and booleans tracking collector/origin viability. There is no disk persistence. The file references process-global PMark configuration objects owned by `XrdNetPMarkCfg.cc`.

## Dependencies and Integration Points
It depends on scheduler/error/trace globals, `XrdNetMsg`, `XrdNetAddrInfo`, `XrdNetUtils`, Linux TCP headers, and socket APIs. It is instantiated only by the PMark configuration implementation and consumed indirectly by xrootd/http/TPC callers through the base `Handle`.

## Risks and Test Signals
Important risks are JSON truncation, unescaped application names, platform-specific missing TCP counters, negative errno reporting mixups, use of `tcpi_bytes_acked` as sent bytes, and correctness of source/destination inversion for PUT-like traffic. Tests should use UDP capture or a fake `XrdNetMsg`, exercise IPv4/IPv6 sockets, collector-only/origin-only/both destinations, long application names, non-Linux behavior, and destructor end-message emission.
