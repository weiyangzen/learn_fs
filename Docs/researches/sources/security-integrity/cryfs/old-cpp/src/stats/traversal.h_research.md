# sources/security-integrity/cryfs/old-cpp/src/stats/traversal.h

Purpose: public declarations for stats traversal helpers over block stores and Rust filesystem blob stores.

Important APIs/types/functions: `cryfs_stats::forEachBlock`, `forEachReachableBlob`, `forEachReachableBlockInBlob`, callback vectors of `std::function<void(const BlockId&)>`.

Control flow: declaration-only header; callers pass a store pointer, root ID where applicable, and callback list.

State and persistence behavior: functions are intended for read-only enumeration of existing blocks and reachable blob/block graphs.

Dependencies and integration points: includes blockstore interfaces and `RustFsBlobStore`; consumed by `main.cpp`.

Risks and test signals: API passes raw pointers and does not encode nullability or ownership. Header typo names `blobtore` in one parameter, harmless for ABI but a readability issue.
