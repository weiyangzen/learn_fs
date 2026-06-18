# File Research: sources/os/linux/linux/fs/pstore/ram_internal.h

## Role

Private header for the ramoops persistent RAM implementation.

## Key Definitions

- `PRZ_FLAG_NO_LOCK`: disables zone locking for contexts such as per-CPU ftrace where lockless writes are desired.
- `PRZ_FLAG_ZAP_OLD`: marks zones whose recovered contents should be wiped after boot-time copyout.
- `struct persistent_ram_zone`: stores physical/virtual mapping data, label, pstore type, flags, buffer pointer and size, ECC parity/header pointers, Reed-Solomon state, correction counters, ECC config, and saved old log.

## API Surface

Declares persistent RAM lifecycle and operations:

- `persistent_ram_new`
- `persistent_ram_free`
- `persistent_ram_zap`
- `persistent_ram_write`
- `persistent_ram_write_user`
- `persistent_ram_save_old`
- `persistent_ram_old_size`
- `persistent_ram_old`
- `persistent_ram_free_old`
- `persistent_ram_ecc_string`

## Research Notes

The header keeps the raw persistent buffer struct opaque to most ramoops code while exposing the zone state needed by `ram.c`.
