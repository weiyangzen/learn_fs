# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsCluster.hh

## Purpose

`XrdCmsCluster.hh` declares the singleton cluster table interface used by cmsd managers, supervisors, peers, and servers. It also defines the CMS node status flags and the `SpaceData` aggregate used for manager/supervisor space reporting.

## Important APIs and types

- Status flags for `Add()`: `CMS_noStage`, `CMS_Suspend`, `CMS_Perm`, `CMS_isMan`, `CMS_Lost`, `CMS_isPeer`, `CMS_isProxy`, `CMS_noSpace`, `CMS_isSuper`, and `CMS_isVers3`.
- Flag groups: `CMS_notServ` and `CMS_hasAlts`.
- `XrdCms::SpaceData` captures total/free space plus read/write and staging free-space/utilization summaries.
- Public cluster methods cover node admission/removal, blacklist updates, broadcast/broadsend, mask lookup, listing, locate/select, monitor threads, reference resets, space summaries, and stats.
- Selection return constants: `NotFound`, `Wait4CBk`, `RetryErr`, and `EReplete`.
- `CmsLSOpts` controls list output shape and desired network interface.
- `SLock()` exposes direct read/write locking for callers that need to coordinate with cluster state.

## Control flow and state shape

The class is a single-instance global, declared as `extern XrdCmsCluster Cluster` in namespace `XrdCms`. The public API is intentionally broad because CMS protocol handlers delegate most cluster-level decisions here. Private helpers split implementation into alternate-manager handling, delayed drop jobs, path/defer logging, bit-count helpers, selection failure formatting, selection algorithms, DFS selection, alternate-manager-list sending, and terminal error formatting.

Core protected state includes `STMutex`, `NodeTab[STMax]`, `NodeWeight[STMax]`, `STHi`, `NodeCnt`, atomic selection counters, fixed-size alternate-manager token storage, and `peerHost`/`peerMask` for peer filtering.

## Dependencies and integration points

The header depends on CMS masks/types, `XrdOucTList`, enum operators, pthread/RW lock wrappers, and atomic counters. It forward-declares major CMS and network types to keep compile dependencies moderate. Callers use this class as the authoritative cluster surface for login, disconnect, request handling, admin/stat operations, and manager coordination.

## Risks

- `SLock()` exposes the internal lock directly; misuse by external callers can deadlock with node-level locks if they do not follow the implementation's lock ordering.
- Many return codes are negative sentinel values rather than typed results, so callers must distinguish wait, retry, complete-error, and not-found outcomes exactly.
- `NodeCnt` is public, but most state is lock-protected. Any direct reader of `NodeCnt` should be reviewed for synchronization assumptions.
- The fixed `AltMans` capacity is tied to `STMax * AltSize`; changes in address formatting or maximum subscribers can have memory/layout effects.

## Test signals

Header/API tests should assert flag combinations, `CmsLSOpts` enum operators, expected public return constants, and compatibility of callers with the declared locking and return-code contracts. Integration tests should verify that the global `XrdCms::Cluster` is the single cluster object used across modules.
