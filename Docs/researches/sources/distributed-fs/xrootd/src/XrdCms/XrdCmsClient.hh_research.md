# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.hh

## Purpose
Declares the CMS client abstraction used by XRootD OFS/cms integrations to locate files, forward metadata operations, prepare files, report server state, and query cluster space.

## Important APIs, Types, and Functions
`XrdCmsClient` defines virtual methods including `Configure`, `Locate`, `Space`, `Forward`, `Prepare`, `Added`, `Removed`, `Resume`, `Suspend`, `Resource`, `Reserve`, `Release`, `Managers`, and `Utilization`. It documents return and callback conventions. It defines `Persona` and mode flags `IsProxy`, `IsRedir`, `IsTarget`, and `IsMeta`, plus plugin factory typedef `XrdCmsClient_t`.

## Control Flow
Implementations are configured once, then receive locate/forward/prepare calls from server code. Methods can complete synchronously, redirect, return data, report errors, or return `SFS_STARTED` to finish later through callback mechanics.

## State and Persistence Behavior
The base class only stores `myPersona`. Derived implementations own cluster connection state. Resource/reserve/release default to no-ops.

## Dependencies and Integration Points
Forward-declares OFS/Ouc/logger/env/prep types and includes no implementation-heavy headers. It is the ABI contract for external CMS plugins and for the built-in `GetDefaultClient()`.

## Risks and Edge Cases
Callback semantics are non-trivial; implementers must use persistent callback objects and avoid non-causal replies. Several default methods silently do nothing or return success-like values, so derived classes must override where behavior is required.

## Test Signals
ABI compatibility tests for plugin loading, derived-class override coverage, return convention tests for locate/forward/prepare, and callback timing tests are important.
