# File Research: sources/os/plan9/9front/sys/src/9/pc/devfloppy.c

Intel 82077A/8272A-compatible floppy disk device driver implementing `#f`.

Key responsibilities:
- Defines supported floppy geometries and controller byte encodings.
- Initializes controller/drive state, DMA channel 2, per-drive track caches, motor state, and watchdog process.
- Exposes `fdNdisk` data files and `fdNctl` control files for up to four drives.
- Handles media change detection, density probing, recalibration, seeking, reading, writing, formatting, eject, reset, and debug controls.
- Performs controller command/result exchange, DMA setup/teardown, interrupt waiting, and error recovery.

Important behavior:
- Reads go through a per-drive track cache; writes invalidate the cached track.
- Media-change handling seeks and reads to clear the change condition, then cycles through compatible densities until one works.
- `floppykproc` turns motors off after roughly five seconds idle.
- Transfer commands cannot cross track boundaries; `floppypos()` truncates lengths accordingly.
- `floppyrevive()` resets the controller when the global state is confused.

Dependencies:
- Depends on PC floppy register constants from `floppy.h`, architecture floppy setup/exec/eject hooks, low DMA helpers, interrupts, and device framework.

Notable risks:
- Controller timing and spin-up delays are empirical.
- Error recovery relies on retry loops and controller reset state.
- Formatting constructs raw per-sector metadata and assumes the selected geometry is correct.
