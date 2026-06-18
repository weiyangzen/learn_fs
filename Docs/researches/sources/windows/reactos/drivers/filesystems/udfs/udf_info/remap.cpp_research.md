# File Research: sources/windows/reactos/drivers/filesystems/udfs/udf_info/remap.cpp

## Purpose

`remap.cpp` implements write verification and bad-sector relocation support for the UDFS driver. It manages an in-memory verify cache of recently written blocks, queues asynchronous verify reads, records blocks that fail write verification, and maps logical sectors through UDF sparing tables or VAT mappings.

## Local Types

- `UDF_VERIFY_ITEM`: one cached block awaiting verification. Stores LBA, CRC, copied block buffer, list link, and queued flag.
- `UDF_VERIFY_REQ_RANGE`: one contiguous verify range.
- `UDF_VERIFY_REQ`: queued work request containing a VCB, temporary buffer, and up to `MAX_VREQ_RANGES` verify ranges.

## Verification Lifecycle

`UDFVInit` initializes `Vcb->VerifyCtx` only when `Vcb->VerifyOnWrite` is enabled and the volume is not in CDR mode. It initializes `VerifyLock`, allocates `StoredBitMap` sized for `LastPossibleLBA`, initializes the list and event, and marks the context initialized.

`UDFVRelease` waits for queued verification to finish, takes `VerifyLock`, removes every cached verify item, clears `VInited`, deletes the resource, frees `StoredBitMap`, and zeroes the context.

`UDFVWaitQueued` waits while `QueuedCount` is nonzero, tracking waiters and pulsing `vrfEvent` when the queue drains.

## Verify Cache Operations

`UDFVStoreBlock` allocates a `UDF_VERIFY_ITEM` plus one block of storage, copies the written block, stores its CRC32, inserts it into the verify list, sets the corresponding `StoredBitMap` bit, and increments `ItemCount`.

`UDFVUpdateBlock` refreshes the stored buffer and CRC for an existing item.

`UDFVRemoveBlock` clears the bitmap bit, unlinks the item, decrements `ItemCount`, and frees the item.

`UDFVWrite` is called after writes. It records the written block range in the verify cache:

- If every block in the range is already cached, it updates each cached item.
- If only some are cached, the active implementation removes those partial overlapping entries and then stores the whole range again.
- If none are cached, it stores every block in the range.
- If the cache exceeds `UDF_MAX_VERIFY_CACHE`, it calls `UDFVVerify` with the lock already held.

`UDFVRead` compares later disk reads against cached write data. For each cached LBA in the read range, it either checks CRC or copies cached data when `PH_READ_VERIFY_CACHE` is requested. On CRC mismatch it restores the cached block into the caller buffer, returns `STATUS_FT_WRITE_RECOVERY`, and marks the bad block in `Vcb->BSBM_Bitmap` when allocation succeeds. Successful reads normally evict verified cache entries unless `PH_KEEP_VERIFY_CACHE` is set; `PH_FORGET_VERIFIED` forces eviction.

`UDFVForget` removes cached verify entries for a range without reading or comparing them.

## Asynchronous Verification

`UDFVVerify` selects cached verify items and groups contiguous LBAs into range requests. It avoids duplicate queueing with each item's `queued` flag, limits each request to `MAX_VREQ_RANGES`, allocates a buffer sized to the largest range, increments `QueuedCount`, and queues `UDFVWorkItem` to `CriticalWorkQueue` outside console builds. With `_CONSOLE`, it executes the work item directly.

`UDFVWorkItem` verifies each queued range. If spare blocks remain, it starts direct-cache mode, calls `UDFTIOVerify` for each range, and ends direct-cache mode. If no spare blocks remain, it logs the exhaustion and falls back to dropping entries from the verify cache by reading cached data with `PH_FORGET_VERIFIED | PH_READ_VERIFY_CACHE`. It frees request memory, decrements `QueuedCount`, and signals `vrfEvent`.

`UDFVFlush` waits for current queued work, forces verification of the remaining cache, then waits again.

## Bad Area and Sparing Support

`UDFCheckArea` reads a candidate area block-by-block or packet-by-packet depending on write-block alignment. Failed reads mark the tested extent as discarded and bad using `UDFMarkSpaceAsXXXNoProtect`.

`UDFRemapPacket` remaps a bad packet through `Vcb->SparingTable`:

- Lazily computes free spare entries when `SparingCountFree == (ULONG)-1`.
- Verifies candidate spare areas with `UDFCheckArea`.
- Marks unusable spare blocks as `SPARING_LOC_CORRUPTED`.
- Aligns the requested LBA to `SparingBlockSize`.
- Detects already remapped packets and can optionally remap a failed spare block when `RemapSpared` is true.
- Assigns the first available spare entry and decrements `SparingCountFree`.

`UDFUnmapRange` releases sparing table entries whose original packet falls fully within a freed range, marking them available again and incrementing `SparingCountFree`.

## Relocation Mapping

`UDFRelocateSector` translates one LBA. With a sparing table, it maps an original packet to the spare packet and preserves intra-packet offset. With VAT, it maps LBAs in the VAT-covered partition through `Vcb->Vat`, returning special sentinel values for next writable address or free entries. Otherwise it returns the original LBA.

`UDFAreSectorsRelocated` checks whether a range intersects a sparing-table remap or requires VAT relocation. For VAT, it treats ranges beyond `NWA` as relocated and scans each VAT entry for non-identity mappings or relevant free entries.

`UDFRelocateSectors` builds an `EXTENT_MAP` for a range whose sectors are relocated. It walks the logical range, calls `UDFRelocateSector` for each block, starts a new extent whenever physical continuity breaks, converts each extent with `UDFExtentToMapping`, and merges them with `UDFMergeMappings`.

## Key Dependencies

This file uses:

- VCB verification state: `Vcb->VerifyCtx`, `VerifyOnWrite`, `CDR_Mode`, `BlockSize`, `BlockSizeBits`, `LastPossibleLBA`.
- Cache/direct I/O helpers: `WCacheStartDirect__`, `WCacheEODirect__`, `UDFTIOVerify`, `UDFTRead`.
- Bitmap helpers: `UDFSetBit`, `UDFClrBit`, `UDFGetBit`, `UDFSetUsedBit`.
- Remap state: `SparingTable`, `SparingCount`, `SparingBlockSize`, `SparingCountFree`, `Vat`, `VatCount`, `NWA`, `Partitions`.
- Extent helpers: `UDFExtentToMapping`, `UDFMergeMappings`, `UDFMarkSpaceAsXXXNoProtect`.

## Risk Notes

The verify cache is protected by `VerifyLock`, but queued items remain in the list with `queued = TRUE` while async work runs. Correctness depends on `QueuedCount`, `vrfEvent`, and the caller-side flush/release protocol waiting before teardown.

`UDFVVerify` marks items queued before allocating all request buffers. If later allocation fails, items can remain marked queued without a work item, which may reduce future verification coverage unless another path clears or removes them.
