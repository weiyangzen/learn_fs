# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devflash.c

## Role

Implements Plan 9 `#F/flash` access to CFI NOR flash, with partition control files and Intel/Sharp Extended command-set programming support.

## Main Data

`Flash` records physical mapping, CFI algorithm id, manufacturer/device ids, write-buffer size, erase regions, boot protection, and offset in concatenated flash space. `FPart` exposes up to 8 named partitions plus `namectl` files. Width/interleaving macros adapt `Funit`/`Fword` access and byte order.

## Control Flow

`cfiquery` enters CFI query mode, validates `"QRY"`, reads algorithm id, total size, write-buffer size, and erase-region geometry. `flashinit` scans `flashN` configs, maps memory, identifies supported algorithms, enables boot protection, and creates whole-device partitions.

The device exposes a top directory and `flash` directory. Reads of data partitions copy mapped flash bytes under read lock and require `eve`. Control reads report offset, size, write-buffer size, ids, and region geometry. Control writes support `erase`, `add`, `remove`, and `protectboot off`. Data writes validate partition bounds, preserve unaligned surrounding bytes, split writes at erase-block and `Maxwchunk` boundaries, invoke the algorithm write routine, and verify with `memcmp`.

Intel/Sharp erase and buffered write commands are implemented with program-power toggling, status polling, error decoding, and reset. AMD/Fujitsu identify is present, but erase/write return unimplemented errors.

## Dependencies

Uses Plan 9 device API, locks, CFI flash command sequences, `flashprogpower`, `isaconfig`, `iseve`, and board memory mappings.

## Risks

Flash writes are destructive and require erase discipline. Boot protection only protects the first erase region unless disabled. AMD/Fujitsu programming is not implemented. Some command parsing uses `atoi`. There is no dynamic partition locking separate from flash lock beyond name nil checks.
