# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSecurity.hh

## Purpose
`XrdNetSecurity.hh` declares a compact authorization helper for host and netgroup based access control.

## Important APIs, Types, and Functions
Public methods add hosts/netgroups, authorize by string or `XrdNetAddr`, merge another instance, and set tracing. Private helpers cache successful hosts and resolve exact host IPs. The class owns an `XrdOucNList` host-pattern anchor, linked netgroup list, OK-host hash, mutex, trace pointer, and check flags.

## Control Flow and State
Instances are mutable policy accumulators. Configuration adds policy, then runtime authorization checks use the cached OK-host hash before slower hostname/netgroup checks.

## Dependencies and Integration Points
It includes XrdOuc hash/list helpers and XrdSys mutexes, and forward-declares address and trace classes. It is used by server and proxy subsystems.

## Risks and Test Signals
`Merge()` deletes its source pointer, so ownership must be explicit. Tests should include policy accumulation, cache behavior, merge ownership, and trace-enabled diagnostics.
