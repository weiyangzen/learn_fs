# sources/distributed-fs/xrootd/src/XrdRmc/XrdRmcSlot.hh

## Purpose

`XrdRmcSlot.hh` defines the compact metadata node used for both cached page slots and attached-file slots in the RMC cache.

## Important APIs, Types, And Functions

- `File()` initializes a file-tracking slot.
- `Find()` scans a hash chain by logical address.
- `Hide()` removes a page slot from a hash bucket and marks it empty.
- `Init()` initializes the page-slot LRU list.
- `Pull()` and `Push()` manipulate LRU list membership.
- `Owner()` overloads remove or attach a page slot to a file-owner list.
- `reRef()` and `unRef()` move slots between referenced and free/LRU positions.
- `SlotState` union holds either an I/O wait queue, `XrdRmcData*`, LRU links, or in-use count depending on slot role.
- Count flags include `lenMask`, `isShort`, `inTrans`, `isSUSE`, and `isNew`.

## Control Flow

The slot is intentionally low-level. `XrdRmcReal` chooses how to interpret union fields based on whether a slot represents page data or a file anchor. LRU and owner operations are intrusive list updates over integer indexes into the slot array.

## State And Persistence

Each slot stores either `Contents` or `Key`, a union status field, owner links, hash link, and count/flags. State is volatile in process memory.

## Dependencies And Integration Points

It forward-declares `XrdRmcData`, `XrdOucCacheIO`, and `XrdSysSemaphore`. The entire RMC implementation depends on the invariants maintained by this class.

## Risks And Edge Cases

- Union fields are role-dependent; accidental use of the wrong interpretation corrupts cache state.
- Inline list operations have minimal validation and assume sentinel/index invariants.
- Count combines length, flags, transit state, and reference accounting in one integer, increasing the chance of mask mistakes.

## Test Signals

Unit tests for slot list operations should initialize small arrays, push/pull/re-reference/unreference slots, manipulate owner lists, and verify hash-chain removal. Integration cache tests are also needed because slot bugs manifest as cache corruption.
