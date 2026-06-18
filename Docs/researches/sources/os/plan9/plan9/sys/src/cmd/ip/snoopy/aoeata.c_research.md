# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/aoeata.c

`snoopy` decoder for AoE ATA command payloads.

Key behavior:
- Parses ATA flag, feature/error, sector count, command/status, and 48-bit LBA.
- Filters on flag, command, feature, sectors, LBA, status, or error.
- Formats ATA fields and terminates protocol walk.

Integration:
- Selected by `aoe.c` command demux value `0`.

Risks and notes:
- Status/error filtering is noted in code as wrong because direction is not available.
- LBA filter stores into `vlv`, but generic numeric compile path primarily uses `ulv`.
