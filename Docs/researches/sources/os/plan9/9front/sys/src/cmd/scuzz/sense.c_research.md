# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/sense.c

Purpose: Formats SCSI sense data for scuzz output.

Key routine:
- `makesense`: prints sense key text, optional decoded ASC/ASCQ text through `scsierror`, and raw sense bytes.

Integration: Uses libdisk's `/sys/lib/scsicodes` mapping and global `bout`.

Risks:
- Assumes `rp->sense[7]` length is trustworthy when printing `8 + sense[7]` bytes.
