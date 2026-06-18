# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/cdr.c

Purpose: Builds MMC and older vendor-specific CD-R/CD-RW SCSI commands.

Key routines:
- MMC: `SRblank`, `SRsynccache`, `SRTOC`, `SRrdiscinfo`, `SRrtrackinfo`.
- Older/vendor-specific: `SRfwaddr`, `SRtreserve`, `SRtinfo`, `SRwtrack`, `SRmload`, `SRfixation`.

Integration: Called by `scuzz.c` command handlers.

Risks:
- `SRtreserve` and `SRwtrack` validate transfer sizes against `rp->lbsize` and `maxiosize`.
- Command encodings are a mix of standard MMC and old device-specific opcodes.
