# File Research: sources/os/plan9/plan9/sys/src/9/kw/flashkw.c

## Role

Kirkwood/SheevaPlug NAND flash driver for Plan 9. It exposes a NAND flash chip through the generic `Flash` interface, including chip identification, erase, page read/write, spare-area ECC handling, and partial-page read-modify-write.

This is directly storage-relevant: it is a raw flash block device implementation, not a filesystem.

## Main Interfaces

- `flashkwlink()`: registers the `"nand"` flash card driver.
- `flashat(Flash *f, uintptr pa)`: probes whether a flash chip exists at a physical address.
- `reset(Flash *f)`: installs `Flash` methods and identifies the chip.
- Internal low-level NAND bus helpers:
  - `nandcmd`, `nandaddr`, `nandread`, `nandreadn`, `nandwrite`, `nandwriten`
  - `nandclaim`, `nandunclaim`
- Flash operations:
  - `erasezone`
  - `read`
  - `write`

## Data Structures

- `Nandreg`: controller registers, including parameter registers and `ctl`.
- `Nandtab`: supported vendor/device table. Includes Hynix `HY27UF084G2M` and a Samsung ID variant.
- `Cache`: single-page software cache with owning `Flash`, page number, page size, and buffer.

## Important Behavior

- Assumes the SheevaPlug NAND interface at a data register address with command/address registers selected by ORing address bits `1` and `2`.
- Uses five-address-cycle NAND page reads and writes.
- Deduces page size, erase block size, and spare bytes from NAND ID byte 4.
- Supports unaligned higher-level reads/writes by reading whole pages into a cache, modifying fragments, then rewriting the page.
- Stores ECC in the last 24 bytes of the spare area: 3 ECC bytes per 256-byte data chunk.
- Reads verify and correct data via `nandecc`/`nandecccorrect`.
- Erase requires erase-block alignment.
- Cache is invalidated on erase and populated after successful reads/writes.

## Dependencies And Assumptions

- Uses Plan 9 flash abstractions from `../port/flashif.h`.
- Uses NAND ECC helpers from `../port/nandecc.h`.
- Depends on Kirkwood SoC mappings in `io.h` and physical constants in `mem.h`.
- Assumes page size and erase size are powers of two.

## Notable Risks

- Partial writes are implemented as read-modify-write on raw NAND; power loss can corrupt the whole page.
- Bad-block handling is mentioned in comments but not implemented here.
- ECC layout is fixed to this driver's convention and may not match all bootloader/Linux layouts.
- Global static page/OOB buffers are not obviously protected against concurrent users.
