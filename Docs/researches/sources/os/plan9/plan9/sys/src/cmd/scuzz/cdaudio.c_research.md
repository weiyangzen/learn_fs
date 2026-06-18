# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/cdaudio.c

SCSI/MMC CD audio command wrappers.

Key behavior:
- Implements pause/resume, stop, play, load/unload, audio status, and get-configuration requests.
- Builds raw SCSI command descriptor blocks and calls `SRrequest()`.
- `SRcdplay()` can play by raw LBA/length or by track number.
- Track-number play reads the TOC with `SRTOC()`, derives track LBAs and lengths, then issues play-by-LBA.

Important details:
- Uses 10-byte and 12-byte MMC command layouts.
- Stores a small static track table for TOC-derived playback.
- If TOC read fails with `STok`, it reports likely empty media through global `bout`.

Filesystem relevance:
- Indirect: operates on SCSI raw device handles opened elsewhere by `scsireq.c`.
