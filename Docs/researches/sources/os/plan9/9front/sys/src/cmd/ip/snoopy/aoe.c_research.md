# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/aoe.c

This snoopy module decodes the common ATA-over-Ethernet header. It exposes filters for shelf, slot, and command, and demuxes command values to `aoeata`, `aoecmd`, `aoemask`, or `aoerr`.

The header parser consumes version/flags, error, major, minor, command, and tag. `p_filter` advances past the AoE header and compares selected fields. `p_seprint` prints version, flags, error, shelf/slot, command, and tag, then chooses the next protocol by command.

The `Proto aoe` registration includes mux table, numeric value format, fields, and default framer.
