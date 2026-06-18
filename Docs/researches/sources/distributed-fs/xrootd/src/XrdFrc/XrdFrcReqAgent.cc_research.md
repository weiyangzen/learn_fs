# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.cc

## Purpose

This file implements `XrdFrcReqAgent`, a per-operation manager for priority request files. It completes request metadata, writes requests to the correct priority queue, cancels requests, lists queue contents, and pings the FRM transfer daemon through a UDP path.

## Important APIs, Types, and Functions

Public methods are `Add()`, `Del()`, `List()`, `NextLFN()`, `Ping()`, and `Start()`. `c2sFN` is a static client-to-server UDP filename initialized once per process.

The constructor chooses a default ping message based on queue type: get, migrate, prestage, put, or generic. `Start()` creates one `XrdFrcReqFile` per priority and optionally inserts registration requests when `XRDCMSCLUSTERID` is set.

## Control Flow

`Add()` clamps priority, sets `addTOD`, copies the instance name, writes to the matching priority `XrdFrcReqFile`, and pings the transfer daemon. `Del()` calls `Can()` on all priority queues for the request id. List methods scan request files and either print LFNs or return one next LFN for streaming proxy listing.

`Ping()` lazily validates the UDP path with `stat()` and sends either the queue-specific ping or an override message through `XrdNetMsg`. `Start()` creates the shared UDP path string, resolves instance name, creates queue directory path, initializes all priority files, and pings if registration records were added.

## State and Persistence Behavior

Agent state is process-local, but queue records are persistent files managed by `XrdFrcReqFile`. Registration records are inserted into every priority queue when cluster id is configured. UDP ping state is cached through static `udpOK`.

## Dependencies and Integration Points

The implementation depends on request files, request structs, FRM utilities, XrdNet UDP messaging, XrdOuc instance names, XrdSys platform headers, and the transfer daemon's `xfrd.udp` control path.

## Risks and Edge Cases

`Ping()` uses static `XrdNetMsg` and `udpOK` shared across all agents, so the first `c2sFN` path dominates. `List()` writes LFNs to `std::cout` while also returning counts, which can be surprising for library callers. If initialization fails after some priority queues are created, earlier allocations are not cleaned up.

## Test Signals

Tests should cover priority clamping, metadata completion, queue file creation per priority, cancellation across priorities, list item formatting, registration insertion from `XRDCMSCLUSTERID`, UDP ping path absence/presence, and start failure cleanup.
