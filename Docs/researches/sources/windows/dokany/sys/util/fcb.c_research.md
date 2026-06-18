# File Research: sources/windows/dokany/sys/util/fcb.c

Dokan FCB lifetime, lookup, rename, and garbage-collection implementation for the Windows kernel driver.

Key responsibilities:
- Defines special internal filenames for keepalive and notification streams.
- Initializes `DokanFCB` objects with `FSRTL_ADVANCED_FCB_HEADER`, paging resources, oplock storage, CCB list state, file size defaults, metrics, and special-file flags.
- Finds or creates FCBs through the per-volume `RTL_AVL_TABLE`, keyed by `UNICODE_STRING` filename.
- Owns open-count decrement and final FCB release through immediate deletion or deferred garbage collection.
- Manages the FCB garbage list, grace-period aging, forced collection, and the dedicated system thread.
- Provides AVL callbacks for filename comparison and node allocation.
- Handles rename-table updates and conflicts with already-existing FCBs.

Important behavior:
- `DokanGetFCB` takes ownership of the filename buffer passed by the caller; new FCBs keep it, failed lookup/init frees it, and existing FCB lookup hands it to `DokanCancelFcbGarbageCollection`.
- Existing FCB reuse cancels pending garbage collection and may update filename casing so case-insensitive lookups do not pin an old case spelling.
- `DokanFreeFCB` first decrements `OpenCount` without the VCB lock so non-final closes can happen safely during nested cache-manager cleanup. Final release then locks VCB and FCB before scheduling or deleting.
- `DokanDeleteFcb` expects VCB and FCB locks to already be held, removes the FCB from the table when requested, frees the filename, tears down oplocks/per-stream contexts/resources, marks the identifier as `FREED_FCB`, unlocks the FCB, and returns it to the lookaside list.
- Deferred GC gives each FCB at least one timer interval of reuse opportunity before deletion. Forced GC deletes all currently scheduled FCBs immediately.
- Rename conflict handling deletes a conflicting FCB if it is already pending GC; otherwise it marks the conflicting FCB `ReplacedByRename` and replaces the AVL table entry.

Dependencies:
- Uses `DokanVCB` state from `dokan.h`: `FcbTable`, `FcbGarbageList`, `FcbGarbageCollectorThread`, `FcbGarbageListNotEmpty`, metrics, and `ValidFcbMask`.
- Depends on global lookaside lists for FCBs and ERESOURCEs.
- Uses Windows kernel primitives: `FsRtlSetupAdvancedHeader`, `FsRtlInitializeOplock`, `RtlInsertElementGenericTableAvl`, `KeWaitForMultipleObjects`, `PsCreateSystemThread`, and resource locks.
- Uses Dokan helpers for VCB/FCB locking, logging, string wrapping, allocation, and identifier checks.

Notable risks:
- The lock contract is strict: deletion paths assume VCB and FCB are locked, while non-final `DokanFreeFCB` intentionally avoids VCB locking.
- `ValidFcbMask` is only a heuristic for rejecting obviously bogus FCB addresses; it cannot prove the pointer is safe.
- GC scheduling uses `NextGarbageCollectableFcb.Flink != NULL` as the “scheduled” marker, so list-entry initialization and clearing are part of the correctness contract.
- Filename buffer ownership is subtle across create, lookup, cancel-GC, rename, and delete paths.
