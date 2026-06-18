# File Research: sources/os/plan9/plan9/sys/src/9/pc/devfloppy.c

Intel 82077A/8272A-compatible floppy controller driver for Plan 9 `#f`.

Key responsibilities:
- Defines floppy device qids, supported disk formats, controller byte-per-sector encodings, and global controller state.
- `floppyreset()` probes platform setup, computes type capacities/track sizes, initializes DMA, allocates drive state/cache buffers, resets motors/controller, and runs platform setup.
- Exposes per-drive `fdNdisk` and `fdNctl`.
- Starts a kernel process to power down idle motors.
- Detects media changes and density by seeking/reading while cycling through compatible formats.
- Uses a per-track cache for reads.
- Validates sector-aligned I/O.
- Implements read/write data paths through seek, DMA setup, command issuance, wait, result validation, and retry.
- Handles control commands: `debug`, `nodebug`, `eject`, `format`, and `reset`.
- Implements controller command send/result receive, sense interrupt, recalibrate, seek, reset/revive, motor control, and interrupt handler.

Important behavior:
- Reads always come through a cached track; writes invalidate matching cached cylinder.
- Media change detection increments qid version and returns `Eio` when an open file sees changed media.
- Transfer retries are bounded by `dp->maxtries`, lower while probing.
- Controller “confused” state triggers full reset and per-drive recalibration.
- `floppywait` synthesizes interrupt handling after timeout for some portable power-management cases.
- Formatting writes per-sector ID records track by track using DMA.

Dependencies:
- Depends on platform-specific floppy hooks declared in comments: port I/O, DMA setup/end/init, `floppyexec`, `floppyeject`, and setup functions from `floppy.h`/platform code.

Notable risks:
- Timing and retries are highly hardware-dependent.
- DMA buffer allocation must satisfy low-memory/alignment constraints.
- Many errors mark controller or drive confused and retry/reset rather than giving detailed cause.
