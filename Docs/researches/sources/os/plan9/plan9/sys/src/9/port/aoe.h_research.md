# File Research: sources/os/plan9/plan9/sys/src/9/port/aoe.h

This header defines ATA-over-Ethernet protocol constants and packet layouts.

Key contents:
- AoE command types for ATA and config/query.
- Config command variants.
- Protocol constants including EtherType `0x88a2`, sector size, version, response/error flags, ATA write and extended-LBA flags.
- `Aoehdr`, the common Ethernet/AoE header.
- `Aoeata`, the ATA command frame.
- `Aoeqc`, the query/config frame.
- `AOEHDRSZ`, `AOEATASZ`, and `AOEQCSZ` offset macros.

Filesystem/storage relevance:
- Shared protocol definition for `devaoe.c`, Plan 9’s AoE block storage initiator.
