# sources/object-store/daos/src/vos/ilog_internal.h

## Purpose
Defines the private durable layout and bit packing for incarnation logs. It is shared by `ilog.c` and recovery/validation code but hidden from normal callers.

## Important APIs, Types, And Functions
Macros partition `lr_magic` into 4 magic bits, 24 version bits, and 4 flag bits. `ILOG_MAGIC_VALID`, version/flag masks, and increment constants drive mutation-version tracking. `struct ilog_tree` holds an allocated array offset plus an `it_embedded` discriminator. `struct ilog_root` overlays inline `ilog_id` and tree metadata, adds `lr_ts_idx`, and stores packed magic. `ilog_empty` checks both embedded and array offset fields. `struct ilog_array` is a flexible-array durable sorted list.

## Control Flow
New roots start with valid magic/version and empty tree fields. First entry is stored inline in `lr_id` and indicated by nonzero `lr_tree.it_embedded` through the union. Multiple entries use `lr_tree.it_root` pointing to an `ilog_array`. Removal can reset to empty or collapse back to inline.

## State And Persistence
All structures are durable ABI. `D_CASSERT` in `ilog.c` ensures `ilog_id` and `ilog_tree` share size and `ilog_root` matches public `ilog_df`. Version wrap preserves magic/flags while cycling version bits.

## Dependencies And Integration
Requires `ilog.h` definitions and `umem_off_t`. Timestamp cache integration uses `lr_ts_idx` via `ilog_ts_idx_get` and VOS timestamp-set wrappers.

## Risks
The union means consumers must respect the embedded/root discriminator; reading the wrong union member can misclassify state. Bit-field packing leaves only four flag bits. Any durable layout change must preserve `sizeof(struct ilog_df)` or migrate data.

## Test Signals
Validation should cover magic recognition, empty/inline/array state transitions, version increment wrap, flags such as corruption, and ABI size assertions.
