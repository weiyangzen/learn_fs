# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/retire_store.c

## Purpose

Implements the persistent I/O retire store backed by `/etc/devices/retire_store`. It decodes retired device paths from an nvlist-backed cache, tracks them in memory, writes updates back through the devcache framework, and answers whether a device path is retired for the current boot.

## Data Model

- On-disk entries are keyed by device path and contain version, magic, and flags.
- `RIO_STORE_F_RETIRED` is persisted; `RIO_STORE_F_BYPASS` is an in-memory boot-time override and is intentionally not encoded.
- In-memory entries are `rio_store_t` nodes containing a duplicated device path, flags, and list linkage.

## Key Interfaces

- `retire_store_init()` handles optional boot-time path override or `/dev/null` bypass, registers nvf file ops, and initializes the in-core list.
- `retire_store_read()` reads the store under the nvf write lock.
- `rio_store_decode()` validates version/magic/flags and appends a retired entry, adding the bypass flag when `ddi_retire_store_bypass` is set.
- `rio_store_encode()` serializes active retired entries to nested nvlists.
- `e_ddi_retire_persist()` adds or refreshes a retired device path, marks the store dirty, and wakes the nvf daemon.
- `e_ddi_retire_unpersist()` removes matching entries and wakes the daemon if the store changed.
- `e_ddi_device_retired()` returns true if the device path itself or one of its parents is in the retired list and not bypassed.

## Locking and Lifetime

- The nvf lock protects the list; decode/free/encode assert write ownership and lookup uses reader ownership.
- List entries own their path string and are freed by `rio_store_free()`.
- `retire_list_free()` frees all in-core entries during devcache lifecycle operations.

## Dependencies

Depends on devcache/nvf APIs, nvlists, kernel lists, boot flags, console input for `RB_ASKNAME`, and DDI path duplication helpers.

## Notes for Future Work

- The bypass mode deliberately reads existing store content so later explicit unretire operations can still remove persisted decisions.
- `e_ddi_device_retired()` treats a retired parent path as retiring descendants by checking exact match or slash boundary.
