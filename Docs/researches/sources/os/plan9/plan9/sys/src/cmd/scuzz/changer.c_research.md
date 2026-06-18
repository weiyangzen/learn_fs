# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/changer.c

SCSI medium-changer command wrappers.

Key behavior:
- `SReinitialise()` issues element status initialization.
- `SRmmove()` moves media from source to destination using a transport element, with optional invert bit.
- `SRestatus()` reads element status data for a given element type into a caller buffer.

Important details:
- Uses 6-byte and 12-byte changer CDBs.
- `SRestatus()` requests all elements by setting start element bytes to `0xFFFF`.

Filesystem relevance:
- Indirect: command helpers for changer devices opened through `/dev/sdXX/raw`.
