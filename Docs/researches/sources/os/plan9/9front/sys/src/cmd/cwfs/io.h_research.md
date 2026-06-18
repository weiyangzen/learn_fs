# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/io.h

SCSI and target constants/types for cwfs I/O support.

Important contents:
- Defines maximum SCSI controllers/targets and network count constants.
- Lists SCSI status/sense-like codes such as `STok`, `STcheck`, `STbusy`, `STtimeout`, and controller/blank/nomem errors.
- Defines `Target`, wrapping a Plan 9 `Scsi*`, controller/target ids, inquiry/sense buffers, a lock, textual id, and ok flag.
