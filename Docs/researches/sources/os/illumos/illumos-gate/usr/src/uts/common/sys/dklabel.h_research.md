# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dklabel.h

## Scope

Complete file read, 277 lines. This header defines the Sun disk label and VTOC on-disk/user-kernel ABI structures used by illumos disk drivers and disk-label tooling.

## Public Surface

The file exports disk-label constants such as `DKL_MAGIC`, `FKL_MAGIC`, `NDKMAP`, `DK_LABEL_LOC`, `DK_LABEL_SIZE`, `DK_MAX_BLOCKS`, and `DK_ACYL`. It conditionally supports `_SUNOS_VTOC_16` and `_SUNOS_VTOC_8`, selecting partition count and label placement at compile time.

It defines `blkaddr_t` and `blkaddr32_t` if `BLKADDR_TYPE` has not already been defined, switching widths based on `_EXTVTOC`. The visible structures are:

- `struct dk_map`: in-memory partition start cylinder and block count.
- `struct dk_map32`: fixed-width on-disk partition map.
- `struct dk_map2`: SVr4 partition tag/flag pair.
- `struct dkl_partition`: VTOC16 partition tag, flag, start sector, and size.
- `struct dk_vtoc`: VTOC payload, with different layouts for 16-slice and 8-slice systems.
- `struct dk_label`: 512-byte disk-label layout ending in `dkl_magic` and XOR checksum.
- `struct fk_label`: DOS floppy label.
- `struct dk_devid`: 512-byte fabricated device-id storage block.
- `DKD_GETCHKSUM()` and `DKD_FORMCHKSUM()` helpers for `struct dk_devid` checksum byte packing.

## Behavior And Integration

There is no executable function body here. Runtime behavior is supplied by disk-label readers, writers, and ioctls that interpret these exact layouts. The structures intentionally preserve on-disk size and field order, including compatibility aliases like `dkl_asciilabel`, `v_timestamp`, and old `_SUNOS_VTOC_8` names such as `dkl_gap1`.

`struct dk_label` is designed to remain at the start of a 512-byte sector; `LEN_DKL_PAD` computes padding from the selected VTOC layout to keep the label structure at `DK_LABEL_SIZE`.

## Dependencies And Invariants

The header depends on illumos integer, address, and byte-order helper types from `sys/isa_defs.h` and `sys/types32.h`; checksum formation also assumes `hibyte`, `lobyte`, `hiword`, and `loword` are available to includers.

Key invariants are ABI layout stability, fixed 32-bit fields for on-disk structures, correct `_SUNOS_VTOC_16` or `_SUNOS_VTOC_8` selection, `DKL_MAGIC` validation, and checksum agreement across the whole label/devid sector. The duplicate `#include <sys/isa_defs.h>` is harmless but visible.

## Risks

Any field reordering or type-width change can corrupt disk labels or break user/kernel ioctl compatibility. `_EXTVTOC` changes `blkaddr_t` width, so callers must distinguish in-memory address capacity from fixed on-disk `blkaddr32_t`. The checksum macros are multi-statement macros without `do { } while (0)`, so use in conditional statements requires care.
