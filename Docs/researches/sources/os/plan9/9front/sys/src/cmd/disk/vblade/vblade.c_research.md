# File Research: sources/os/plan9/9front/sys/src/cmd/disk/vblade/vblade.c

## Purpose
Implements a virtual ATA over Ethernet target serving one or more backing files as AoE shelves/slots.

## Key Behavior
- Parses per-blade options for initialization/raw mode, virtual size, AoE shelf.slot address, config string, and one or more ethernet interfaces.
- Uses a `Vbhdr` header at the start of non-raw backing files to persist magic, byte size, shelf.slot address, config length, and config data.
- `checkfile()`, `chkvblade()`, `recheck()`, and `savevblade()` validate/persist backing metadata and determine usable LBA count after header overhead.
- Opens Plan 9 ethernet AoE data endpoints by connecting clone files to EtherType `0x88a2`; one process is launched per interface.
- Serves AoE config commands: read, test, prefix, set, and force-set, including config-length validation and firmware/buffer metadata.
- Serves ATA commands: identify device, 28/48-bit reads, and 28/48-bit writes. Unsupported commands return ATA abort.
- Synthesizes IDENTIFY data with model `Plan 9 Vblade`, serial `serial#`, version `2`, and 28/48-bit LBA capacity fields.
- Checks sector count against interface MTU-derived limit and validates accesses against the virtual max LBA.
- Swaps Ethernet source/destination addresses and sets response shelf/slot in replies; broadcasts initial config discovery packets.
- Supports multiple blades and dispatches incoming requests by shelf/slot, including wildcard broadcasts.

## Interfaces And Dependencies
- Uses Plan 9 `thread`/`proccreate`, ethernet device files, `<ip.h>` byte helpers, and `<fis.h>` ATA status/error constants.
- Uses `aoe.h` for wire structures and constants.

## Notes
The code uses processes rather than threads for blocking network reads/writes. Raw mode skips the persistent `Vbhdr` and exposes the whole backing file; non-raw mode reserves 128 sectors for metadata.
