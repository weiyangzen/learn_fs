# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver_lyr.c

## Purpose

`driver_lyr.c` implements illumos Layered Driver Interface support. It lets kernel consumers open lower devices by dev_t, path, or devid; tracks who opened what; exposes read/write/ioctl/strategy/property/event APIs through `ldi_handle_t`; records STREAMS multiplexing relationships; and propagates device events through LDI callbacks and device contracts.

This is the central file for safe kernel-to-kernel device stacking.

## Core Data Structures

The LDI keeps two reference-counted hash tables:

- `ldi_ident_hash`: maps caller identity to `struct ldi_ident`, keyed by module id plus optional dip, dev_t, or major.
- `ldi_handle_hash`: maps target vnode plus identity to `struct ldi_handle`.

`ldi_init()` initializes both hash tables and the event callback list. Handles hold both the identity and target vnode. The handle type records whether the target is a STREAMS vnode or a character/block callback device.

## Identity And Handle Lifetime

Identities can be created from:

- module linkage: `ldi_ident_from_mod()`,
- anonymous genunix identity: `ldi_ident_from_anon()`,
- STREAMS queue: `ldi_ident_from_stream()`,
- dev_t: `ldi_ident_from_dev()`,
- devinfo pointer: `ldi_ident_from_dip()`,
- major number: `ldi_ident_from_major()`.

All identities are released with `ldi_ident_release()`. Internally, `ident_alloc()`, `ident_hold()`, and `ident_release()` preserve one shared identity per key.

Handles are allocated by `handle_alloc()` after a successful specfs open. Duplicate opens of the same vnode by the same identity share a handle and increment its reference count. `handle_release()` removes the handle from the hash on the last reference, releases the vnode and identity, and updates `ldi_handle_hash_count`.

## Opening Devices

Target vnodes are resolved by:

- `ldi_vp_from_dev()` using `e_ddi_hold_devi_by_dev()` and `makespecvp()`.
- `ldi_vp_from_name()` using global-zone pathname lookup when root is mounted, or `resolve_pathname()` before root or for OBP/devfs paths.
- `ldi_vp_from_devid()` using `ddi_lyr_devid_to_devlist()`, then revalidating the devid against the held devinfo node to avoid races with replaced devices.

Public opens are `ldi_open_by_dev()`, `ldi_open_by_name()`, and `ldi_open_by_devid()`. All flow through `ldi_open_by_vp()`, which requires a specfs block/char vnode, rejects missing `cb_ops`, performs `VOP_OPEN(..., FKLYR, ...)`, handles clone-open vnode replacement, and creates the LDI handle.

`ldi_close()` performs `VOP_CLOSE(..., FKLYR, ...)`, nulls matching event callback handle references, and releases the handle even if close fails.

## I/O And Device Operations

The file exposes LDI wrappers for common lower-device operations:

- `ldi_read()` and `ldi_write()` dispatch to `cdev_*` for cb devices or `strread`/`strwrite` for STREAMS.
- `ldi_ioctl()` normalizes kernel ioctl mode to `FNATIVE | FKIOCTL`, supplies a temporary `rvalp` when callers pass NULL, and translates kernel `I_PLINK` into `_I_PLINK_LH` for STREAMS layered-handle linking.
- `ldi_poll()` dispatches to character-device or STREAMS polling.
- `ldi_strategy()`, `ldi_dump()`, `ldi_devmap()`, `ldi_aread()`, and `ldi_awrite()` support cb devices, with async I/O restricted to devices that have block-style strategy support.
- `ldi_putmsg()` and `ldi_getmsg()` provide STREAMS message send/receive helpers.
- `ldi_get_dev()`, `ldi_get_otyp()`, `ldi_get_devid()`, and `ldi_get_minor_name()` expose handle metadata.

`ldi_get_size()` derives byte size from block `Nblocks`/`nblocks` plus `blksize` or `device-blksize`, then falls back to `Size`/`size` properties.

## Property Support

`ldi_prop_op()` and the typed lookup/get helpers locate the associated dip through the common snode or by dev_t. They first allow the driver's dynamic `prop_op()` to override values and then fall back to normal DDI property interfaces.

Typed property wrappers include:

- `ldi_prop_lookup_int_array()`
- `ldi_prop_lookup_int64_array()`
- `ldi_prop_lookup_string_array()`
- `ldi_prop_lookup_string()`
- `ldi_prop_lookup_byte_array()`
- `ldi_prop_get_int()`
- `ldi_prop_get_int64()`
- `ldi_prop_exists()`

`i_ldi_prop_op_typed()` rejects zero-length properties and properties whose length is not a multiple of the element size. String helpers validate null termination and repack concatenated string arrays into the pointer-array format expected by callers.

## Usage Walker

`ldi_usage_count()` returns the number of open handle records. `ldi_usage_walker()` walks handle buckets and reports target/source relationships via a callback. It resolves target dips from snodes or dev_t, and source dips from identity state. When an identity only names a driver or major, it conservatively reports all current instances of that source driver as possible users of the lower device.

This is used for device usage observability and devinfo snapshot-style consumers.

## STREAMS Link Tracking

`ldi_mlink_lh()` creates a temporary `file_t` for a lower vnode so STREAMS persistent linking can operate on an LDI handle.

`ldi_mlink_fp()` records successful STREAMS links as LDI handle relationships. Normal links identify the upper side from the STREAMS queue and dev_t; persistent links identify only the upper major. For layered-handle persistent links, it adjusts common snode and file reference counts so the lower stream remains open while linked.

`ldi_munlink_fp()` reverses this state, clears `SMUXED`, finds the matching handle, releases it, and releases the temporary identity.

## Event Framework

The file supports two event families:

- native LDI events such as `LDI_EV_OFFLINE`, `LDI_EV_DEGRADE`, and `LDI_EV_DEVICE_REMOVE`,
- NDI event-service callbacks passed through `ddi_add_event_handler()`.

`ldi_ev_get_cookie()` returns native cookies from a static table or asks NDI for a cookie. `ldi_ev_register_callbacks()` validates callback versions, registers NDI handlers when needed, and adds callback records to the protected callback list. `ldi_ev_remove_callbacks()` removes records safely even during callback-list walks.

The event lock is recursive by design because layered drivers may call back into LDI, including `ldi_close()`, from notify/finalize callbacks.

Native event propagation uses:

- `ldi_invoke_notify()` to negotiate synchronous events with registered layered drivers and roll back earlier notifies with finalize callbacks if a later callback vetoes.
- `ldi_ev_notify()` to combine device-contract negotiation with LDI notify propagation.
- `ldi_invoke_finalize()` to deliver final event disposition.
- `ldi_ev_finalize()` to finalize both device contracts and LDI callbacks.

## Dependencies

This file depends on specfs, devinfo hold/release APIs, DDI property APIs, STREAMS internals, vnode operations, kernel file allocation, device contracts, NDI event services, module name/major translation, and devid conversion helpers in the devid cache path.

## Notable Invariants And Audit Notes

- LDI handles require a valid specfs block or character vnode and valid target `cb_ops`.
- Handle lifetime is independent of close success; after `ldi_close()` the handle is no longer usable.
- Event callback records can survive handle close with `lec_lhp == NULL` so finalize can still inform consumers after notify-triggered close.
- Callback-list walkers use `le_walker_next` and `le_walker_prev` so callbacks can unregister themselves or others safely.
- Property helpers must release any dip hold on all success and fallback paths; this is a repeated pattern worth preserving in edits.
- `ldi_get_size()` relies on block-size properties being powers of two and asserts that invariant before shifting.
