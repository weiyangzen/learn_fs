# File Research: sources/windows/winfsp/src/sys/meta.c

## Purpose

`meta.c` implements a small nonpaged metadata cache used by WinFsp for cached per-file metadata such as security descriptors, directory info, stream info, and EA data. Items are indexed by generated integer IDs and expire by timeout or capacity pressure.

## Main Contents

- `FSP_META_CACHE_ITEM` stores list linkage, hash linkage, backing buffer pointer, item index, expiration time, and refcount.
- `FSP_META_CACHE_ITEM_BUFFER` prefixes returned item buffers with a backpointer and size.
- A static assert verifies that the public metadata item header size matches the actual buffer layout.
- Internal helpers:
  - `FspMetaCacheDereferenceItem`
  - `FspMetaCacheLookupIndexedItemAtDpcLevel`
  - `FspMetaCacheAddItemAtDpcLevel`
  - `FspMetaCacheRemoveIndexedItemAtDpcLevel`
  - `FspMetaCacheRemoveExpiredItemAtDpcLevel`
- Public API:
  - `FspMetaCacheCreate`
  - `FspMetaCacheDelete`
  - `FspMetaCacheInvalidateExpired`
  - `FspMetaCacheReferenceItemBuffer`
  - `FspMetaCacheDereferenceItemBuffer`
  - `FspMetaCacheAddItem`
  - `FspMetaCacheInvalidateItem`

## Data Structure

The cache is one page:

- Header fields live in `FSP_META_CACHE`.
- Hash buckets fill the rest of the page.
- `ItemList` tracks insertion/expiration order.
- `ItemBuckets` provide lookup by item index.
- Items and item buffers are separately allocated.

## Control Flow

- `FspMetaCacheCreate` returns success with a null cache if capacity, max item size, or timeout is zero.
- `FspMetaCacheAddItem`:
  - rejects oversize items,
  - allocates an item and buffer,
  - copies caller data under exception handling,
  - removes one expired/oldest item if capacity is exceeded,
  - assigns a monotonically increasing nonzero item index,
  - inserts into the list and hash table.
- `FspMetaCacheReferenceItemBuffer` looks up an item, increments its refcount under the spin lock, and returns the user-visible buffer pointer plus optional size.
- `FspMetaCacheDereferenceItemBuffer` recovers the hidden header from the buffer pointer and drops the item reference.
- Invalidations remove an item from index/list ownership, then dereference outside the spin lock.

## Synchronization

- Hash/list/cache counters are protected by `MetaCache->SpinLock`.
- Refcounts use interlocked operations.
- Memory is freed only when the final reference drops.

## Notable Details

- Item index zero is reserved as invalid; wrap from `UINT64_MAX` returns to `1`.
- Expiration is checked only against the head of `ItemList`, so the list is expected to be ordered by insertion and expiration time.
- `FspMetaCacheDelete` invalidates all items by passing `(UINT64)-1LL` as expiration time, then frees the cache page.
