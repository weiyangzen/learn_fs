# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_ctl.c

## Purpose

`ctfs_ctl.c` implements the per-contract `ctl` and `status` files. `ctl` accepts contract control ioctls, while `status` returns common or detailed contract status to libcontract consumers.

## File Shape

- Size: 336 lines, 8,264 bytes.
- SHA-256: `0b87d8d455f1379550aedf36a7c7a0588370ac51ef4cc302b2562db4aab1ade1`.
- Public creators: `ctfs_create_ctlnode()` and `ctfs_create_statnode()`.
- Operation vectors: `ctfs_tops_ctl` and `ctfs_tops_stat`.

## Core Behavior

- Control and status nodes store a pointer to the parent cdir's contract; the parent directory provides the transitive contract hold.
- `ctfs_ctl_access()` permits write access only to the contract owner or to the regent process for abandoned inherited contracts. Read or execute access to `ctl` is denied.
- `ctfs_ctl_open()` requires exactly `FWRITE | FOFFMAX` and passes the control access check.
- `ctfs_ctl_ioctl()` implements `CT_CABANDON`, `CT_CACK`, `CT_CNACK`, `CT_CNEWCT`, `CT_CQREQ`, and `CT_CADOPT`, copying event IDs from userland where needed and calling the corresponding contract subsystem functions.
- `ctfs_stat_ioctl()` implements `CT_SSTATUS`. For `CTD_COMMON`, it fills a status struct under `ct_lock`; for detailed levels up to `CTD_ALL`, it asks the contract type for an nvlist, packs it natively, copies it to the caller if the provided buffer is large enough, and updates `ctst_nbytes`.
- Shared getattr logic sets file type, link count, zero size, ctime from contract creation, and atime/mtime from the event queue.

## Dependencies And Contracts

- Relies on libcontract ioctl constants and `STRUCT_*` model macros for native/32-bit status structs.
- Uses contract core APIs: abandon, ack/nack, newct, qack, adopt, common status, and type-specific status callbacks.
- Uses `nvlist_pack()` with `NV_ENCODE_NATIVE` for detailed status payloads.

## Maintenance Notes

`ctl` is write-only and control-oriented; `status` is read-only but still ioctl-driven. Permission rules in `ctfs_ctl_access()` are part of contract ownership semantics and should stay in sync with contract lifecycle behavior.
