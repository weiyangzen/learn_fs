# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClustID.cc

## Purpose

`XrdCmsClustID.cc` implements the process-global registry that maps CMS cluster identifiers to `XrdCmsClustID` objects. It is used by `XrdCmsCluster` to group ordinary servers, managers, peers, and alternate managers under a stable cluster id, to derive node masks by cluster id, and to keep a small alternate-manager table for a cluster.

## Important APIs and functions

- `XrdCmsClustID::AddID(const char *cID)` normalizes a bi-compatible cluster id by stripping everything through the last space, interns it in the static `XrdOucHash<XrdCmsClustID> cidTab`, and returns the existing or newly allocated cluster-id object.
- `XrdCmsClustID::Find(const char *cID)` applies the same normalization and looks up an existing cluster id without creating it.
- `XrdCmsClustID::Mask(const char *cID)` returns the accumulated `SMask_t` for a cluster id, or zero when unknown.
- `XrdCmsClustID::AddNode(XrdCmsNode *nP, bool isMan)` adds a node mask to the cluster id. For non-manager/server entries it only ORs the mask. For manager or peer alternates it also records the node pointer in the bounded alternate array and enforces a shared slot number.
- `XrdCmsClustID::Exists(XrdLink *lp, const char *nid, int port)` scans alternate entries and delegates identity matching to `XrdCmsNode::isNode`.
- `XrdCmsClustID::RemNode(XrdCmsNode *nP)` removes either a plain server mask or an alternate node pointer and returns the replacement alternate primary candidate if any.

## Control flow

The file is built around three local statics: `cidMtx`, `cidTab`, and `cidFree`. `AddID()` duplicates the normalized id before locking, lazily refreshes `cidFree`, and calls `cidTab.Add(..., Hash_keep)`. When the key already exists, it frees the duplicate string and returns the existing object; when the key is new, it installs the previously prepared `cidFree` and creates a fresh spare object for the next insertion.

`AddNode()` is the key mutator. Non-manager additions are cheap: the node mask is merged into `cidMask` and no alternate table slot is consumed. Manager/peer additions validate capacity (`altMax == 8`) and slot consistency using `nP->ID(iNum)`, then append the node pointer and update `ntSlot` and `cidMask`. `RemNode()` is the inverse: plain servers clear the node mask immediately, while managers/peers are removed from the compacted alternate array, with `cidMask` cleared only when no alternate entries remain.

## State and persistence behavior

State is entirely in-memory and process-global. `cidTab` owns id-to-object lookup, each object owns a duplicated `cidName`, and each object tracks `cidMask`, `ntSlot`, `npNum`, and up to eight `XrdCmsNode *` alternates. There is no persistent storage. State changes are protected by `cidMtx` for add/find/mask/existence/add-node paths; `RemNode()` mutates object fields without taking `cidMtx` itself, so callers must provide a safe context or accept the risk of concurrent mutation.

## Dependencies and integration points

The implementation depends on `XrdCmsNode` for masks and identity checks, `XrdCmsTrace`/`Say` for logging, `XrdOucHash` for string-key interning, and `XrdSysMutex` for registry locking. Its main integration point is `XrdCmsCluster::Add()`, `AddAlt()`, `Remove()`, and `getMask(const char *)`, which use cluster ids for alternate manager replacement, duplicate-login rejection, and cluster mask lookup.

## Risks

- `RemNode()` lacks an internal `cidMtx` guard even though it updates `cidMask`, `npNum`, and `nodeP`; reviewers should confirm all callers already hold a lock that serializes with `AddNode()` and `Exists()`.
- The alternate table hard limit is eight entries. Overflow rejects additional alternate managers/peers and logs an error; large deployments need explicit test coverage for this behavior.
- Cluster id normalization is repeated in `AddID()`, `Find()`, and `Mask()` and depends on the last space in the id string. Inputs with trailing spaces or unexpected embedded whitespace could alias ids unexpectedly.
- `cidFree` is allocated as a spare global object and never reclaimed during process lifetime; this is intentional process-global cache behavior but should be considered when sanitizers report reachable allocations.

## Test signals

Useful tests would exercise repeated `AddID()` for the same id returning the same object, cluster ids with and without compatibility prefixes, server-only mask accumulation and removal, manager alternate insertion up to and past `altMax`, slot mismatch rejection, `Exists()` duplicate detection, and alternate removal returning the replacement node used by `XrdCmsCluster::Remove()`.
