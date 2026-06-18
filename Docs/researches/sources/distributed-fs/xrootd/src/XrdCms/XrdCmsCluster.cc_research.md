# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.cc

## Purpose

`XrdCmsCluster.cc` implements the singleton `XrdCms::Cluster`, the central runtime node table for cmsd. It admits and removes subscribers, tracks managers/peers/servers, sends CMS protocol messages, locates files, selects redirect targets, reports statistics, maintains alternate-manager lists, and monitors load/reference counters.

## Important APIs and functions

- `XrdCmsCluster::Add()` admits a new node, reconnects an existing node, installs alternate managers through `XrdCmsClustID`, redirects or bumps old nodes when the table is full, updates peer masks and cluster state, and returns the node locked.
- `AddAlt()` adds a manager/peer alternate under an existing cluster id and can replace a dropped primary with a live alternate.
- `BlackList()` applies or removes blacklist status on matching nodes and can send disconnect requests.
- `Broadcast()` and `Broadsend()` send CMS requests to node masks, with `Broadcast()` returning an unqueried mask and `Broadsend()` choosing one eligible node round-robin.
- `Locate()` finds current or potential locations for a path, using `Cache.Paths`, file-state cache entries, DFS mode, and broadcast state queries.
- `Select(XrdCmsSelect &)` is the high-level file redirect selector for read/write/meta/replica/staging flows.
- `Select(SMask_t, ...)` is a lower-level selector for an already computed mask, used when callers only need host/port resolution.
- `Remove()`, `Drop()`, and the local `XrdCmsDrop` job class implement delayed, immediate, and asynchronous node teardown.
- `SelNode()`, `SelbyCost()`, `SelbyLoad()`, `SelbyLoadR()`, and `SelbyRef()` implement the actual scheduling policies.
- `Space()`, `Stats()`, and `Statt()` summarize cluster space and XML-like statistics.
- `MonPerf()` periodically asks nodes for usage; `MonRefs()` periodically resets selection reference counters.

## Control flow

Node admission starts in `Add()`. It scans `NodeTab[STMax]` for an existing identity, a free slot, and bump candidates. Existing disconnected nodes are rehooked. Manager/peer entries that share a known cluster id can enter as alternates through `AddAlt()`. If capacity is exhausted, ordinary incoming nodes may be redirected using `sendAList()`, or old entries may be removed and replaced. New nodes are constructed, tied to a `XrdCmsClustID`, marked with status flags, counted, and used to update `CmsState`.

Removal uses a two-step design. `Remove(reason, node, immed)` normalizes lock ordering with a stack `theLocks` helper, marks nodes offline, disconnects live links, substitutes a live alternate manager when possible, or schedules a delayed `XrdCmsDrop`. `Drop()` validates the node id/instance pair before actually clearing `NodeTab`, removing alternate-manager text entries, lowering `STHi`, invalidating `Cache` entries, and deleting the node directly or via an asynchronous delete job.

File lookup and selection split path availability from redirect choice. `Locate()` consults `Cache.Paths`, optionally handles wildcard current-server listings, and either uses DFS-specific checks or asks candidate nodes for state. `Select(XrdCmsSelect &)` computes allowed, primary, and staging masks based on path export information, cached file state, write/read semantics, tried-node masks, refresh/new-file/replica flags, and DFS behavior. It then calls `SelNode()` unless a wait or terminal error is required.

`SelNode()` applies network interface constraints, optional affinity packing, space requirements, local-node preference, peer fallback, and delay/error construction. The `Selby*()` helpers scan `NodeTab` under `STMutex`, skip unreachable/offline/bad/overloaded/full nodes, update selector reason flags, increment selection counters, and choose by peer cost, load, randomized load weight, or reference count.

## State and persistence behavior

All cluster state is in memory. `NodeTab[STMax]` stores active node pointers; `NodeCnt`, `STHi`, `peerHost`, and `peerMask` summarize occupancy and peer filtering; `AltMans`, `AltMend`, and `AltMent` store fixed-width alternate manager redirect tokens; `SelWtot`, `SelRtot`, and `SelTcnt` are atomic selection counters; and `NodeWeight[STMax]` is scratch state for randomized load selection.

`STMutex` protects node table structure and most node-state traversal. The code frequently swaps the global table lock for a per-node lock with `g2nLock()` to avoid holding the global lock across node-specific actions. Persistence is delegated elsewhere: file/path knowledge is in `XrdCmsCache`, global state reporting in `XrdCmsState`, and scheduled jobs in `XrdScheduler`.

## Dependencies and integration points

This file integrates with `XrdCmsConfig`, `XrdCmsNode`, `XrdCmsCache`, `XrdCmsBaseFS`, `XrdCmsClustID`, `XrdCmsState`, `XrdCmsRRQ`, `XrdCmsBlackList`, `XrdCmsRole`, `XrdCmsSelect`, and CMS protocol structs. Configuration fields drive selection delays, scheduling policy, space thresholds, peer-delay policy, service minimums, and role behavior.

## Risks

- Locking is complex. `Broadcast()` intentionally drops and reacquires `STMutex` while holding a node reference; removal and deletion correctness depends on reference counts and lock conversion ordering.
- `SelbyLoadR()` builds cumulative weights but does not call the `RefCount` macro on the selected node, unlike the other selectors. That means randomized load scheduling may not update per-node reference counters consistently.
- `SelbyLoadR()` constructs `std::uniform_int_distribution<int>(1, totWeight)` without an explicit `totWeight > 0` guard. Normal positive `P_fuzz + (100 - load)` values should make eligible weights positive, but extreme config or future changes could make this fragile.
- In `Drop()`, peer removal uses `peerHost &= nP->NodeMask`, which preserves only the dropped peer bit rather than clearing it; this deserves review against intended peer-mask semantics.
- Alternate manager text in `AltMans` uses fixed-width blank-padded slots. Formatting changes must preserve `AltSize` assumptions and rotation logic.

## Test signals

High-value tests include admission/reconnection/displacement cases; manager alternate replacement on primary loss; blacklist apply/remove with disconnect request generation; broadcast behavior with offline and failed-send nodes; DFS and non-DFS locate/select paths; write conflict cases for duplicate/readonly/no-replica files; peer fallback after local delay thresholds; selection counter behavior across all scheduling policies; drop cancellation when node instances change; and stats output sizing with many nodes.
