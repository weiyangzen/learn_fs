# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsUtils.hh

## Purpose

`XrdCmsUtils.hh` declares CMS configuration and plugin utility functions used by manager/server setup code.

## Important APIs and Types

The static API consists of `loadPerfMon()`, `ParseMan()`, `ParseManPort()`, and `SiteName()`. Private helpers `Display()` and `SInsert()` support implementation-only DNS display and sorted manager-list insertion.

## Control Flow

The declared functions are intended for configuration parse time: load optional perf monitor, parse manager endpoint and port tokens, merge manager list entries, and later translate numeric site IDs back to text.

## State and Persistence Behavior

Although the header does not expose member state, implementation maintains process-global site mappings and returns caller-owned allocations/lists. `ParseMan()` may modify its `hSpec` and `hPort` arguments in place.

## Dependencies and Integration Points

It forward-declares `XrdCmsPerfMon`, `XrdOucStream`, `XrdOucTList`, `XrdSysError`, and `XrdVersionInfo`, limiting include churn for configuration users.

## Risks and Edge Cases

The API contract requires mutable C strings and caller-managed memory, which is easy to misuse. Optional output `sPort` can be updated even when no manager list is returned.

## Test Signals

Header-level integration tests should compile consumers with only forward declarations, while implementation tests validate ownership and in-place parsing expectations.
