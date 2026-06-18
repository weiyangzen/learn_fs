# File Research: sources/windows/reactos/drivers/filesystems/ntfs/btree.c

Read status: complete file, 2030 lines.

This file implements an in-memory B-tree abstraction for NTFS filename indexes, plus conversion to and from on-disk `$INDEX_ROOT`, `$INDEX_ALLOCATION`, and `$BITMAP` state. It is central to directory mutation support.

Key entry points:
- `CreateBTreeFromIndex()` parses an index root, optionally recursing into index allocation nodes via `CreateBTreeNodeFromIndexNode()`.
- `CreateEmptyBTree()` creates a root node with a dummy end key for new directories.
- `NtfsInsertKey()` inserts filename keys in sorted order, descends into children, handles child split propagation, and marks nodes dirty.
- `SplitBTreeNode()` splits oversized non-root nodes, creates a right-hand sibling, promotes a median key, and installs dummy end keys.
- `DemoteBTreeRoot()` turns an oversized root into a child of a new root dummy key.
- `UpdateIndexAllocation()` and `UpdateIndexNode()` allocate index records, update child VCN references, create index buffers, and write dirty nodes back to `$INDEX_ALLOCATION`.
- `CreateIndexRootFromBTree()` serializes the root node into a resident index root.
- `AllocateIndexNode()` extends the index allocation and `$I30` bitmap and returns the new node VCN.
- `DestroyBTree*()` and `DumpBTree*()` manage/debug tree memory.

Important dependencies:
- Attribute layer: `FindAttribute`, `ReadAttribute`, `WriteAttribute`, `SetResidentAttributeDataLength`, `SetNonResidentAttributeDataLength`, `AttributeDataLength`.
- File-record mutation: `AddIndexAllocation`, `AddBitmap`, `UpdateFileRecord`.
- NTFS fixup support: `FixupUpdateSequenceArray`, `AddFixupArray`.
- Filename collation uses `RtlCompareUnicodeString`; case sensitivity follows the create/open flags.

Notable behavior and risks:
- Several write paths are explicitly incomplete: attribute lists, creating new nodes in some cases, adding a missing bitmap in `AllocateIndexNode()`, and replacing hardcoded layout math.
- `CreateIndexBufferFromBTreeNode()` uses hardcoded USA offset/count and first-entry offset values.
- `SplitBTreeNode()` uses a hardcoded `HalfSize = 2016`, so split balance assumes common 4096-byte records.
- `CreateBTreeKeyFromFilename()` does not zero the whole key before assigning fields, so `LesserChild` can be uninitialized unless callers overwrite it.
- `CreateIndexBufferFromBTreeNode()` checks size using `CurrentNodeEntry->Length` before copying the current key into that buffer location, which weakens overflow detection.
