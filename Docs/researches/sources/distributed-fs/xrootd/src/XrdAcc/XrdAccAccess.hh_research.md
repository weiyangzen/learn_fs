# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.hh

## Purpose

`XrdAccAccess.hh` declares the default access-control implementation and its table structures. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAccess_ID` stores named set-rule selectors for name, group, host, org, role, and user plus associated capabilities. `XrdAccAccess_Tables` groups hash tables for groups, hosts, netgroups, orgs, roles, sets, templates, and users, plus domain/default/fungible capability lists and inclusive/exclusive set lists. `XrdAccAccess` implements `XrdAccAuthorize` with `Access()`, `Audit()`, `Test()`, `Resolve()`, and `SwapTabs()`.

## Control Flow

The header captures the table-swap architecture: `XrdAccConfig` builds a fresh `XrdAccAccess_Tables`, then `SwapTabs()` publishes it. `Access()` reads the published tables under `Access_Context`.

## State and Persistence Behavior

`XrdAccAccess_Tables` owns hash/list allocations and deletes them in its destructor. `XrdAccAccess_ID::Export()` transfers owned strings/caps from a stack definition into heap state by nulling the original. `XrdAccAccess` holds current tables, host-resolution flags, the reader-writer lock, and an audit object pointer.

## Dependencies and Integration Points

It depends on audit, authorization, capability, security entity, `XrdOucHash`, `XrdSysXSLock`, and platform types. `XrdAccConfig` is a friend because it needs to set the private auditor and tables.

## Risks and Edge Cases

Ownership semantics are manual and pointer-heavy; incorrect table construction can double-free or leak capabilities. `S_Hash` destructor is expected to delete `SXList` and `SYList`, making list ownership coupled to hash ownership. Public inheritance from `XrdAccAuthorize` means ABI changes affect plugins.

## Test Signals

Unit tests should exercise table construction/destruction, `XrdAccAccess_ID::Applies()`, export ownership transfer, and concurrent `SwapTabs()` with active `Access()` calls.
