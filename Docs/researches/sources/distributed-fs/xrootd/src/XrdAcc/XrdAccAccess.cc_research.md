# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.cc

## Purpose

`XrdAccAccess.cc` implements the default XRootD authorization engine. It loads the default authorization object, computes privileges for authenticated entities against path capabilities, applies auditing, resolves hosts when needed, and atomically swaps access tables built by configuration. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccDefaultAuthorizeObject()` verifies plugin version compatibility, configures `XrdAccConfiguration`, and returns `Authorization`. `XrdAccAccess::Access()` accumulates capabilities from defaults, domain/host/netgroup/user, group/org/role, and inclusive/exclusive set rules. `Access2()` combines positive and negative masks and audits/tests an operation. `Audit()` maps operations to names and routes grant/deny records. `Resolve()` converts IP-like host strings through `XrdNetAddrInfo`. `SwapTabs()` atomically swaps `XrdAccAccess_Tables`. `Test()` maps `Access_Operation` to required `XrdAccPrivs`. `XrdAccAccess_ID::Applies()` tests set-rule selectors.

## Control Flow

`Access()` starts by creating or retrieving an `XrdAccEntity` attribute iterator. It prefers `Entity->eaAPI` `request.name` over `Entity->name`. It locks `Access_Context` shared, applies exclusive set rules first and returns on the first match, then conditionally resolves the host and accumulates default, host/domain, netgroup, fungible user, specific user, group, org, role, and inclusive set capabilities. The lock is released before `Access2()` tests and audits. Table refresh uses `SwapTabs()` under exclusive lock, then purges group caches.

## State and Persistence Behavior

Authorization tables are process-memory hash tables and lists protected by `XrdSysXSLock`. `hostRefX` and `hostRefY` avoid DNS work unless configured rules require host names. The global config owns the current authorization instance. No privileges persist beyond in-memory config refreshes.

## Dependencies and Integration Points

The file integrates with `XrdAccConfig`, `XrdAccEntity`, `XrdAccCapability`, `XrdAccGroups`, `XrdSecEntity`, `XrdSecEntityAttr`, `XrdNetAddrInfo`, `XrdSysPlugin`, and `XrdOucHashVal2`.

## Risks and Edge Cases

`Test()` declares a `need[]` table only through operation indexes 0-14, but `AOP_LastOp` is 16 and the enum includes `AOP_Stage` and `AOP_Poll`; stage/poll checks can read past the table. `Audit()` assumes `Entity` and `Entity->eaAPI` are valid. Host resolution can be expensive and occurs under the shared access-table lock when exclusive rules need it. Negative privileges are global within accumulated caps and can remove bits granted by other matching rules. Exclusive set rules return immediately on the first match.

## Test Signals

Tests should cover every `Access_Operation`, especially stage and poll; all selector types; exclusive rule ordering; inclusive rule accumulation; negative privilege subtraction; token username override; host-domain matching; DNS resolution gating; audit-on-grant/deny; and hot table swap under concurrent access.
