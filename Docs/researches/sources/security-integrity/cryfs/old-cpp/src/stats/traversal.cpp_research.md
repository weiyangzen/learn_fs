# sources/security-integrity/cryfs/old-cpp/src/stats/traversal.cpp

Purpose: traversal helper implementations for `cryfs-stats`.

Important APIs/types/functions: `forEachBlock`, `forEachReachableBlob`, `forEachReachableBlockInBlob`, `BlockStore::forEachBlock`, `RustFsBlobStore::load`, `RustDirBlob::AppendChildrenTo`, and `DataBlob::allBlocks`.

Control flow: `forEachBlock` forwards every block ID to callbacks. `forEachReachableBlob` recursively visits root and directory children by block ID. `forEachReachableBlockInBlob` loads a blob and invokes callbacks for every block listed by `allBlocks`.

State and persistence behavior: read-only traversal of block/blob stores; recursion depends on persisted directory entries and blob child references.

Dependencies and integration points: uses Rust fsblobstore types, fspp directory entries, `cpputils::dynamic_pointer_move`, `boost::none`, and `ASSERT`.

Risks and test signals: recursive traversal can stack-overflow on very deep trees and has no cycle guard; it assumes directory child lists and lookups remain internally consistent. No automated tests here validate corrupted stores.
