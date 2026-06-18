# File Research: sources/os/linux/linux-stable/fs/pstore/ram.c

## Summary
Implements the `ramoops` pstore backend. It partitions reserved persistent RAM into dmesg, console, ftrace, and pmsg persistent RAM zones, reads old contents after reboot, writes new crash/console/ftrace/pmsg data, and registers the resulting backend with pstore.

## Main Responsibilities
- Parse module parameters, reserved-memory names, platform data, and device-tree properties.
- Allocate persistent RAM zones for dmesg records, console log, pmsg log, and ftrace records.
- Add ramoops-specific dmesg headers containing timestamp and compression state.
- Read old persistent records and expose them as pstore records.
- Write dmesg, console, ftrace, and pmsg records to appropriate PRZs.
- Erase records by zapping PRZs and freeing old buffers.
- Register a platform driver and optional dummy platform device for module-parameter configuration.

## Key Interfaces
- `ramoops_probe()` configures zones and calls `pstore_register()`.
- `ramoops_remove()` unregisters pstore and frees zones.
- `ramoops_pstore_read()`, `ramoops_pstore_write()`, `ramoops_pstore_write_user()`, and `ramoops_pstore_erase()` implement backend operations.
- `ramoops_init_przs()` allocates arrays of dump/ftrace zones.
- `ramoops_init_prz()` allocates single console/pmsg zones.

## Important Behavior
Dmesg zones are circularly selected by `dump_write_cnt`. Only `record->part == 1` is accepted, so a single crash is not split across multiple ramoops records. Before writing a dmesg record, the target PRZ is zapped so stale data is not appended ahead of the new header.

Ftrace can use either one shared zone or per-CPU zones. Per-CPU ftrace read builds a temporary PRZ and merges all per-CPU logs using `pstore_ftrace_combine_log()`.

Device-tree parsing supports modern reserved-memory bindings and compatibility behavior for older Chromebooks where ramoops was not under `reserved-memory`. Sizes are rounded down to powers of two before zone creation.

## State and Synchronization
Most persistent buffer synchronization lives in `ram_core.c`. `ramoops_context` tracks zone arrays, read/write counters, sizes, flags, ECC config, and the embedded `struct pstore_info`.

## Cross-File Interactions
Uses `persistent_ram_*()` helpers from `ram_core.c` and declarations from `ram_internal.h`. Registers with the pstore platform layer in `platform.c`, which then exposes records through `inode.c`.

## Risks
The backend depends on a correctly reserved physical memory range. Bad sizing can leave no room for a requested zone. Dmesg headers are required for recovered dmesg records; records without valid headers are zapped and skipped.
