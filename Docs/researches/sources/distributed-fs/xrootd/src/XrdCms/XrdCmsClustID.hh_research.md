# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.hh

## Purpose

`XrdCmsClustID.hh` declares `XrdCmsClustID`, the small registry entry type used to associate a cluster id string with a server mask and a bounded set of alternate manager/peer nodes. The header exposes the operations needed by the cluster table while hiding the registry and locking details in the `.cc` file.

## Important APIs and types

- `class XrdCmsClustID` is the registry entry.
- Static factory/lookups: `AddID()`, `Find()`, and `Mask()`.
- Node membership: `AddNode()`, `RemNode()`, and `Exists()`.
- State queries: `Avail()`, `IsEmpty()`, `IsSingle()`, and `Slot()`.
- Internal constants and fields: `altMax = 8`, `cidMask`, `cidName`, `ntSlot`, `npNum`, and `nodeP[altMax]`.

## Control flow and semantics

The constructor initializes an empty id with no mask, no name, no assigned slot, zero alternate nodes, and a null-filled alternate pointer array. The destructor frees only `cidName`; it does not own or delete any `XrdCmsNode` pointers. Inline methods are intentionally simple predicates used by cluster admission and removal: `Avail()` checks whether another alternate fits, `IsEmpty()` and `IsSingle()` describe alternate-table occupancy, and `Slot()` exposes the primary cluster table slot shared by alternate manager entries.

## State and persistence behavior

`XrdCmsClustID` stores transient process state. Its only heap-owned field is `cidName`, allocated with `strdup()` in the implementation and freed with `free()` in the destructor. Node pointers are borrowed references into `XrdCmsCluster`/`XrdCmsNode` lifetime management.

## Dependencies and integration points

The header forward-declares `XrdLink` and `XrdCmsNode`, includes `XrdCmsTypes.hh` for `SMask_t`, and uses C library allocation helpers. It is included by `XrdCmsCluster.cc` to associate logins with cluster ids and by any component needing `XrdCmsClustID::Mask()`.

## Risks

- Borrowed `XrdCmsNode *` values make lifetime ordering important. Deletion must go through cluster removal/drop paths that remove node pointers before freeing nodes.
- The fixed `altMax` is not configurable from this header, so any alternate-manager scaling change requires code changes and tests.
- The API does not expose explicit locking semantics; callers cannot tell from the header which methods lock internally.

## Test signals

Header-level test signals are mostly integration tests through `XrdCmsCluster`: successful alternate insertion, alternate overflow, cluster slot mismatch, and cleanup on node removal. Static analysis should also verify that `cidName` allocation/free conventions stay paired.
