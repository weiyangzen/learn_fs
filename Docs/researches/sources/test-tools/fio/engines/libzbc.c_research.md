# sources/test-tools/fio/engines/libzbc.c

## Purpose
Implements a synchronous libzbc engine for host-aware/host-managed SMR or ZBC/ZAC devices. It performs direct sector-based reads/writes/flushes and implements fio zoned-block-device callbacks by translating libzbc zone data into fio's `zbd_zone` model.

## Important APIs, Types, And Functions
`struct libzbc_data` stores the libzbc device handle, device model, sector count, and max-open sequential requirement. Important functions are `libzbc_open_dev()`, `libzbc_get_dev_info()`, `libzbc_get_file_size()`, `libzbc_get_zoned_model()`, `libzbc_report_zones()`, `libzbc_reset_wp()`, `libzbc_move_zone_wp()`, `libzbc_finish_zone()`, `libzbc_get_max_open_zones()`, `libzbc_rw()`, and `libzbc_queue()`.

## Control Flow
Open validates that the fio file is a block or char device, chooses read/write flags based on workload, opens with SCSI/ATA libzbc drivers, and caches device info in `td->io_ops_data`. Size is `nr_sectors << 9`. Zone reporting allocates a libzbc zone array, calls `zbc_report_zones()`, converts starts/lengths/write pointers from sectors to bytes, maps types and conditions, and treats read-only/offline/unknown conditions as offline. Queue handles read/write through `zbc_pread()`/`zbc_pwrite()`, sync through `zbc_flush()`, and trim through fio's zbd trim helper.

## State And Persistence
One libzbc device handle is stored per thread. Persistent changes include writes, flushes, zone resets, zone finishes, and write-pointer movement by writing filler data. The engine does not cache normal I/O data and invalidation is a no-op.

## Dependencies And Integration Points
Depends on libzbc, fio `zbd` types/helpers, and raw direct device access. It supplies fio's zoned callbacks for model, report, reset, finish, max-open, and write-pointer movement.

## Risks
All I/O lengths and offsets are converted with `>> 9`, so callers must honor 512-byte sector alignment. Some functions assume `td->io_ops_data` is already open. Error handling negates libzbc return values and logs sense-key details when available. Zone capacity is set equal to zone length because ZBC/ZAC lacks an explicit capacity field.

## Test Signals
Test block and char devices, host-aware/host-managed model detection, size discovery, zone reporting conversions, reset-all and per-zone reset, finish-zone, write-pointer movement, read/write short transfer errors, flush, trim in zbd mode, max-open-zone limit handling, and open/close cleanup.
