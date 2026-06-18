# File Research: sources/os/linux/linux/fs/pstore/ram.c

## Role

Implements the `ramoops` pstore backend. It partitions a reserved RAM region into persistent RAM zones for dmesg, console, ftrace, and pmsg records, then registers those zones as a pstore backend.

## Configuration

Supports module parameters and device tree/platform data for:

- reserved memory address/name/size;
- memory mapping type;
- dmesg record size;
- console, ftrace, and pmsg sizes;
- max kmsg dump reason;
- deprecated `dump_oops`;
- ECC size;
- flags such as per-CPU ftrace.

## Read Path

- `ramoops_pstore_open()` resets per-type read counters.
- `ramoops_pstore_read()` returns records in order:
  - dmesg zones with valid `====<time>-<C|D>` headers;
  - console zone;
  - pmsg zone;
  - ftrace zone(s), combining per-CPU records when configured.
- Adds ECC status text to exposed records using `persistent_ram_ecc_string()`.

## Write Path

- `ramoops_pstore_write()` handles console, ftrace, and dmesg records.
- Dmesg writes accept only `record->part == 1` to avoid split crash reports across multiple RAM records.
- Before writing a new dmesg record, the target zone is zapped so the header starts at offset zero.
- `ramoops_pstore_write_user()` handles pmsg writes directly from userspace.
- `ramoops_pstore_erase()` frees old copies and zaps the selected zone.

## Zone Initialization

- `ramoops_init_przs()` creates arrays of persistent RAM zones for dmesg and ftrace.
- `ramoops_init_prz()` creates single console or pmsg zones.
- `ramoops_probe()` parses platform data/DT, rounds zone sizes down to powers of two, maps reserved memory, builds pstore frontend flags, allocates dmesg buffer, and registers with pstore.
- `ramoops_remove()` unregisters pstore and frees all zones.

## Device Tree and Dummy Platform Device

- `ramoops_parse_dt()` reads reserved-memory resource and properties such as `record-size`, `console-size`, `ftrace-size`, `pmsg-size`, `ecc-size`, `flags`, and `max-reason`.
- `ramoops_register_dummy()` creates a platform device from module parameters when no DT/platform device exists.

## Research Notes

`ram.c` contains policy and pstore integration; `ram_core.c` contains the persistent circular buffer/ECC mechanics. Ramoops is deliberately read-only from VFS perspective but writes during crash/console/pmsg/ftrace paths into reserved RAM.
