# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdr.c

SCSI/MMC CD-R and older CD writer command wrappers.

Key behavior:
- Implements blanking, sync cache, read TOC, read disc info, read track info.
- Implements older writer commands: first writable address, reserve track, track info, write track, media load, and fixation.
- Validates write and reservation sizes against `rp->lbsize` and `maxiosize`.
- Updates `rp->offset` after successful track writes.

Important details:
- Commands are constructed directly into local CDB byte arrays.
- Read-style commands fill caller-provided buffers.
- Write-style/control commands set `rp->data.write = 1` even when no payload is transferred.

Filesystem relevance:
- Indirect: provides media-writing operations over raw SCSI device files managed by the surrounding scuzz tool.
