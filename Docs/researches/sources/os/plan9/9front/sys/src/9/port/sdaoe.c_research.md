# File Research: sources/os/plan9/9front/sys/src/9/port/sdaoe.c

`sd` backend exposing ATA-over-Ethernet devices discovered through the AoE filesystem/device interface.

Key responsibilities:
- Tracks AoE controllers by path with global linked-list lookup/add/delete.
- Probes configured AoE targets from `aoedev`, including shorthand expansion to `#æ/aoe/...`.
- Issues AoE discover commands and waits for `ident` files to appear.
- Reads ATA identify data, extracts model/serial/firmware and sector count, and builds SCSI inquiry data.
- Opens the AoE `data` file for block reads/writes.
- Implements `verify`, `online`, `bio`, `rio`, `rctl`, `probew`, `clear`, and top-level control hooks for `SDifc`.
- Uses `sdfakescsi()` and `sdfakescsirw()` for SCSI request emulation.

Important behavior:
- Drive size or serial changes set `drivechange` and increment `vers`.
- AoE errors `Echange` or `Enotup` during I/O clear `u->sectors` to force rediscovery/online handling.
- Flush-cache SCSI commands are recognized but return check condition because `flushcache()` is stubbed to `-1`.
- PNP probing sends `nofail on` after establishing the target.

Notable risks:
- Controller deletion has a suspicious loop update expression using `x = c->next`; changes should inspect this path carefully.
- Depends heavily on external AoE device files and error strings.
