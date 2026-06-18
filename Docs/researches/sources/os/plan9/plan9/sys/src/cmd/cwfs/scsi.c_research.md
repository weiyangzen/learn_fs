# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/scsi.c

SCSI command wrapper over Plan 9 `scsi(2)`/`sd(3)` interfaces.

Key responsibilities:
- `scsiinit()` initializes controller/target table, locks, IDs, and inquiry/sense buffers.
- `doscsi()` sends a command via `scsi()`, and on failure issues request-sense via `scsicmd()`.
- `sense2stcode()` maps sense bytes to internal `ST*` status codes.
- `scsiexec()` records failed commands for diagnostics.
- Command helpers: `scsitest`, `scsistart`, `scsiinquiry`, `scsireqsense`.
- `scsiprobe()` tests, spins up if needed, requests sense, runs inquiry, and marks target ok.
- `scsiio()` locks/probes target, retries commands up to 10 times, handles blank reads by zero-filling, and returns status.
- `newscsi()` connects an opened `Scsi*` handle to a `Target`.

Important interactions:
- Used by `juke.c` for robotics commands.
- Device target selection comes from `Device.wren.ctrl`, `.targ`, and `.lun`.

Research notes:
- The comments note that LUNs are not implemented in sd(3), but the code still carries LUN bits in SCSI commands.
- `lastcmd`/`lastcmdsz` are diagnostic globals for failed request-sense output.
- `scsiverbose` is set externally to 1 in `scsiinit()`.
