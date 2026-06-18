# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/emul64var.h

## Role

`emul64var.h` is the private kernel header for the `emul64` emulated SCSI host bus adapter. It defines driver-local constants, packet/transport accessor macros, soft-state layout, target backing-store bookkeeping, hotplug state, reset notification state, and external support routines.

## Main Definitions

- Provides shorthand constants and request helpers such as `TRUE`, `FALSE`, `UNDEFINED`, `CNUM()`, `TGT()`, `LUN()`, `REQ_TGT_LUN()`, packet state/stat extraction, and SCSI packet flag translation through `EMUL64_SET_PKT_FLAGS()`.
- Defines driver timing and queue constants: retry delay, initial soft-state slots, reset waits, non-interrupt polling delay, timeout margin, `EMUL64_NDATASEGS`, `SHUTDOWN_THROTTLE`, and `CLEAR_THROTTLE`.
- Sets default SCSI options to parity, disconnect/reconnect, sync, tagged, fast, and wide operation.
- Defines hotplug soft-state bits: `EMUL64_SS_OPEN`, `EMUL64_SS_DRAINING`, `EMUL64_SS_QUIESCED`, and `EMUL64_SS_DRAIN_ERROR`.
- Defines `emul64_rng_overlap_t` for checking whether requested disk block ranges overlap no-write ranges.
- Defines sparse backing storage with `blklist_t`, storing only non-zero written blocks in an AVL tree, and `emul64_nowrite_t`, a linked list of disk ranges where writes are ignored.
- Defines `emul64_tgt_t`, the per-target state: SCSI address, target list link, no-write ranges, geometry, inquiry data, data block AVL tree and locks, and error injection fields.
- Defines `struct emul64_slot` for timeout deadlines and `struct emul64_reset_notify_entry` for registered reset callbacks.
- Defines the main `struct emul64` soft state: SCSI HBA transport and devinfo, interrupt cookie, revision fields, timeout id, SCSI option arrays, reset delay, initiator id, suspend flag, per-target capability/sync data, register pointer, request/response/hotplug locks, max LUN/sector arrays, reset notification list, backoff, hotplug state, condition variable, taskq, and target list.

## Locking And Contracts

The header centralizes mutex access with `EMUL64_REQ_MUTEX()`, `EMUL64_RESP_MUTEX()`, `EMUL64_HOTPLUG_MUTEX()`, `EMUL64_MUTEX_ENTER()`, and `EMUL64_MUTEX_EXIT()`. It also includes `_NOTE()` annotations documenting request and response mutex protection for queue, mailbox, slot, and response fields that are expected by implementation files.

## External Interfaces

The file declares BSD/backing-store setup routines (`emul64_bsd_init()`, `emul64_bsd_fini()`, `emul64_bsd_get_props()`), block-range helpers (`emul64_overlap()`, `emul64_bsd_blkcompare()`), and global tunables/statistics such as `emul64debug`, `emul64_nowrite_count`, `emul64_collect_stats`, and taskq limits.
