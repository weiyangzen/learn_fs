# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/cdaudio.c

Purpose: Implements MMC CD audio and mechanism helper commands for the scuzz SCSI shell.

Key routines:
- `SRcdpause`, `SRcdstop`: pause/resume and stop playback.
- `_SRcdplay`: raw play by LBA and length.
- `SRcdplay`: optionally maps a track number to LBA/length by reading TOC before calling `_SRcdplay`.
- `SRcdload`: load/eject media or changer slot.
- `SRcdstatus`: read mechanism status.
- `SRgetconf`: read MMC configuration.

Integration: Uses `ScsiReq` and `SRrequest` from `scsireq.c`, constants from `scsireq.h`, and `SRTOC` from `cdr.c`.

Risks:
- Static `tracks[100]` assumes TOC fits.
- Stack command buffers are safe only because `SRrequest` is synchronous.
