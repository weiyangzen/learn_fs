# sources/storage-engines/foundationdb/fdbserver/kvstore/DeltaTree.h

## Purpose
Implements packed, memory-mappable binary search trees whose nodes store delta-compressed items. Provides `DeltaTree` and `DeltaTree2` templates for balanced builds, lazy decoding, seeking/iteration, insertion into reserved free space, and deletion marking.

## Important APIs, Types, and Functions
- `lessOrEqualPowerOfTwo`, `perfectSubtreeSplitPoint`, and `perfectSubtreeSplitPointCached` compute balanced subtree root positions.
- `DeltaTree<T, DeltaT>` stores a packed header plus variable-sized nodes with 16-bit or 32-bit child offsets, delta payloads, item counts, byte accounting, height metadata, and `largeNodes`.
- `DeltaTree::DecodedNode`, `Mirror`, and `Cursor` lazily reconstruct items, cache decoded child/ancestor links, seek, iterate, insert, and hide deleted nodes.
- `DeltaTree::build` and `buildSubtree` serialize sorted items into a near-perfect compressed BST using previous/next ancestor prefix sources.
- `DeltaTree2<T, DeltaT>` uses tree-relative child offsets, `DecodeCache`, index-based decoded nodes, partial caches, cursor tree switching, insertion, deletion, byte-deleted tracking, and zeroing of unused build space.
- `DeltaTree2::Cursor` resolves items from delta/partial cache, navigates child indices, supports seeks and movement, restores deleted equal items, and appends new child nodes when free bytes allow.

## Control Flow
Build chooses a balanced root for each subtree, selects the better left/right prefix source, writes a delta, recursively serializes children, records offsets, and computes free bytes. Reads create decoded nodes on demand and traverse by comparing target keys with reconstructed `T` values. Public seek variants then move forward/backward to hide deleted nodes. Insert finds the would-be parent, restores deleted equal items, or computes base candidates, checks free space, writes the new node at the tree end, links parent offsets/cache indices, updates counts, and tracks max height. Erase marks nodes deleted rather than compacting.

## State and Persistence Behavior
The raw tree is intended to live in a memory-mappable byte region. Header fields, node offsets, delta bytes, and deleted flags persist in that region. Decode mirrors/caches are transient and rebuildable. Insertions consume `nodeBytesFree`; deletions leave bytes because descendants may borrow prefixes from deleted ancestors. `DeltaTree2::build` zeroes unused space.

## Dependencies and Integration Points
Depends on Flow, Arena, FDB types, and server knobs. The item and delta types supply compare, common-prefix calculation, delta sizing/writing/application, partial-cache support, deleted flags, and debug strings.

## Risks and Edge Cases
Packed layout, `#pragma pack`, pointer arithmetic, variable-sized deltas, and offset width choices are high-risk. `DeltaTree` offsets are node-relative while `DeltaTree2` offsets are tree-relative. `numItems` is `uint16_t`. Deleted nodes remain as prefix bases. Decode-cache vector reallocation requires reacquiring references. Cursor movement assumes valid state. Older hinted seek is documented as broken/slower.

## Test Signals
KV-store tests should cover build/seek iteration, prefix compression round trips, deletion hiding, insertion/free-space behavior, deleted-item restoration, small vs large node modes, cache reuse after tree switching, memory accounting, and reload from raw bytes.
