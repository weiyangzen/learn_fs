# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/juke.c

Purpose: Implements cwfs support for SCSI optical jukeboxes, especially HP-style robotics with WORM/labeled-WORM sides. It bridges `Device` trees to a private `Juke` structure, controls medium movement, mounts sides into drives, and exposes block read/write/size operations.

Key structures:
- `Side`: per-disc-side state, including shelf element, drive slot, loaded/unloaded status, rotation side, ordinal label, timing, native block geometry, and Plan 9 block geometry.
- `Juke`: global jukebox state: side table, drive table, offline flags, robotics `Scsi*`, element geometry, rotation/double-sided flag, and linked-list membership.

Important behavior:
- `querychanger()` opens the changer through `sdof()`/`openscsi()`, installs SCSI target state with `newscsi()`, reads changer geometry, creates side records, and records initial positions.
- `jukeinit()` validates the `j(...)` device layout, registers console commands, attaches drive devices, and stores the `Juke*` in jukebox and side devices.
- `wormunit()` is the central loader. It locks a side, selects a drive with `bestdrive()`, moves media via `mmove()`, waits for drive readiness, opens the drive data file, discovers block geometry, and for labeled worms verifies the label.
- `wormlabel()` reads or writes the label block on `Devlworm`, checks `Labmagic`, detects byte-swapped labels, validates side ordinal, and calls `cmd_wormreset()`/`panic()` on serious mismatches.
- `wormread()`/`wormwrite()` translate cwfs logical blocks to `pread`/`pwrite` against the loaded drive, with bounds checks and error counters.
- `wormsizeside()` and `wormsidestarts()` walk composite device trees to map a side number to its size/start offsets, including jukes embedded inside mcat/mlev/mirror/cw devices.
- `wormprobe()` periodically unloads inactive spinning sides after `TWORM`.

Operational interfaces:
- Console commands: `wormreset`, `wormeject`, `wormingest`, `wormoffline`, `wormonline`.
- SCSI commands issued directly here include mode sense, read element status, and move medium.

Notable details:
- `SCSInone` is defined as `SCSIread` because move-medium has no payload but still uses the scsi wrapper.
- `bestdrive()` prefers a drive already holding the other side of the same platter, then an empty online drive, then the oldest eligible loaded drive.
- `wormsize()` hides the last block from `Devlworm` users because it stores the label.
- The file assumes serialized robotics changes through `Juke` and `Side` locks; label I/O temporarily unlocks the side because `wormread()` re-enters `wormunit()`.
