# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsSupervisor.cc

## Purpose

`XrdCmsSupervisor.cc` implements the supervisor endpoint used by a supervisor node to communicate with exactly one redirector through a Unix-domain socket named `olbd.super`. It creates an `XrdInet` listener, normalizes supervisor-specific configuration, and accepts redirector connections for CMS protocol processing.

## Important APIs and Functions

`XrdCmsSupervisor::Init(const char *AdminPath, int AdminMode)` prepares the socket and listener. It uses `XrdNetSocket::socketPath()` to build an admin socket path, creates `NetTCPr`, applies `Config.myDomain`, binds the path, and forces supervisor subscription/drop behavior. `Start()` accepts connections forever, allocates an `XrdCmsProtocol` for `"redirector"`, attaches it to the `XrdLink`, calls `Process()`, and closes the link.

## Control Flow

Initialization fails early if the socket path cannot be created, if `XrdInet` allocation fails, or if bind fails. On success it sets `Config.SUPCount = 1`, `SUPLevel = 0`, and `DRPDelay = 0`, then flips `superOK`. Runtime flow is a single infinite accept loop; each connection is handled synchronously before the next accept.

## State and Persistence Behavior

State is static: `superOK` records readiness and `NetTCPr` owns the listener. The Unix socket path is persistent in the admin filesystem namespace until cleaned by socket/bind handling. There is no explicit shutdown or listener deletion in this file.

## Dependencies and Integration Points

The code depends on `XrdInet`, `XrdLink`, `XrdCmsConfig`, `XrdCmsProtocol`, tracing/error globals, and `XrdNetSocket`. It integrates supervisor nodes with redirector protocol processing and mutates global CMS config to match supervisor semantics.

## Risks and Edge Cases

The accept loop has no exit path, backoff, or error logging for repeated accept failures. It assumes only one redirector is allowed but enforces that mostly by serial synchronous processing, not explicit peer identity. Configuration mutation in `Init()` has broad process impact and must happen before other code relies on the original drop-delay or subscriber-count settings.

## Test Signals

Integration tests should verify socket path creation, listener bind failures, forced config values, successful allocation/processing of a redirector protocol, and cleanup/close behavior after a client disconnects.
