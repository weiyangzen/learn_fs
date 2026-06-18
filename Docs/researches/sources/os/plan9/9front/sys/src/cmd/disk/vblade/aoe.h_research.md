# File Research: sources/os/plan9/9front/sys/src/cmd/disk/vblade/aoe.h

## Purpose
Defines ATA over Ethernet protocol constants and packet structures for `vblade`.

## Key Contents
- Enumerates AoE command classes (`ACata`, `ACconfig`), query-config subcommands, and error codes.
- Defines Ethernet AoE type `0x88a2`, fixed sizes, version, response/error flags, and ATA command flag bits.
- `Aoehdr` models the Ethernet/AoE common header with destination/source MACs, type, version flags, shelf/slot, command, and tag.
- `Aoeata` models AoE ATA command fields: flags, error/features, sector count, command/status, LBA, and reserved bytes.
- `Aoeqc` models query-config response/request fields including buffer count, firmware version, sector count, command, and config string length.

## Notes
The header assumes `Eaddrlen` is defined before inclusion; `vblade.c` provides it locally because the userspace code does not get the kernel definition.
