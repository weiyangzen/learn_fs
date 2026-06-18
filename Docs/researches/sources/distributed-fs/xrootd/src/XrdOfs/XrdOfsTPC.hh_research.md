# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPC.hh

## Purpose

`XrdOfsTPC.hh` declares the base OFS TPC object and its static control interface. It is the shared contract used by authorization objects, queued copy jobs, and OFS open/sync paths that need a polymorphic TPC handle.

## Important APIs, Types, and Functions

The central type is `class XrdOfsTPC`, containing public `XrdOfsTPCInfo Info`, virtual `Del()` and `Sync()`, and nested request context `Facts` with key, LFN, PFN, origin, destination, user security entity, error object, and environment. Static APIs configure and operate TPC: `AddAuth`, `Allow`, `Authorize`, `credPath`, `Init`, `Require`, `Restrict`, `Start`, and `Validate`. `reqALL`, `reqDST`, and `reqORG` select which side an auth requirement applies to.

## Control Flow

This header has no executable flow, but it defines the call graph shape. OFS request code creates `Facts`, calls `Authorize()` for source-open rendezvous validation or `Validate()` for destination write-side copy setup, then later calls virtual `Sync()` and `Del()` on the returned object.

## State and Persistence Behavior

Instances carry a reference count (`Refs`) and queue flag (`inQ`), while static members carry process-wide auth requirements, allow lists, path restrictions, credential path, and access-authorizer pointer. The state is in-memory and lifetime-managed by `Del()` implementations in derived classes.

## Dependencies and Integration Points

The header depends on `XrdOfsTPCInfo` and forward-declares OFS, OUC, ACC, and SEC types to keep compile coupling low. It is included by `XrdOfsTPCAuth` and `XrdOfsTPCJob`, and the `Facts` structure is the narrow bridge from OFS request parsing into TPC logic.

## Risks and Edge Cases

`Refs` and `inQ` are `char`, which is compact but risky if lifetime rules change or unusually many references are added. Because `Facts` stores borrowed pointers, callers must keep request strings, environment, error object, and security entity valid through the immediate call.

## Test Signals

Compile tests should cover inclusion from auth/job/prog implementations. Behavioral tests should exercise base-pointer deletion, waiting `Sync()` paths, and static configuration setup before and after `Start()`.
