# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/scsi.c

Purpose: SCSI adapter layer for cwfs, using Plan 9 `scsi(2)`/sd interfaces rather than old direct host-adapter commands.

Key structures:
- `Ctlr`: controller table containing `Target target[NTarget]`.
- `Target` fields are defined elsewhere but used here for locking, id strings, inquiry/sense buffers, target numbers, ok flag, and attached `Scsi*`.

Important behavior:
- `scsiinit()` initializes all controller/target records, allocates inquiry/sense buffers, and enables SCSI verbosity.
- `newscsi()` attaches an opened `Scsi*` handle to a cwfs `Device` target.
- `scsitarget()` maps a `Device`’s `wren.ctrl`/`wren.targ` to the static controller table.
- `doscsi()` executes a command with `scsi()`, and on failure sends request-sense to classify the error.
- `sense2stcode()` and `scsireqsense()` translate sense keys and additional sense codes into `STok`, `STblank`, `STcheck`, or hard errors.
- `scsiprobe()` tests readiness, handles reset/unit attention, attempts spin-up for becoming-ready devices, runs inquiry, and marks the target ok.
- `scsiio()` lazily probes, retries commands up to ten times, treats blank reads as zero-filled success, and prints retry diagnostics.

Notable details:
- LUN is preserved in `cmd[1]` and reused for request-sense.
- `lastcmd` is saved for sense diagnostics.
- This file is critical for `juke.c` robotics commands.
