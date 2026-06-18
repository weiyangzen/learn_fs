# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/io.h

SCSI support constants and `Target` structure declaration.

Key responsibilities:
- Defines controller/target limits:
  - `MaxScsi = 4`
  - `NTarget = 16`
  - `Maxnets = 8`
- Defines SCSI status codes such as `STok`, `STcheck`, `STblank`, `STtimeout`, `STharderr`, and others.
- Defines `Target`, containing:
  - `Scsi *sc`
  - controller/target identifiers
  - inquiry/sense buffers
  - qlock
  - id string
  - availability flag.

Research notes:
- Included by SCSI, jukebox, main, and memory/buffer code where SCSI target state or networking limits are needed.
