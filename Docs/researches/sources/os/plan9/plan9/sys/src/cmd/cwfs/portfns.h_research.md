# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/portfns.h

Shared function prototype header for cwfs.

Key contents:
- Prototypes for:
  - auth operations
  - config parsing and device lifecycle
  - console commands and console 9P wrappers
  - cwfs/cached-WORM operations
  - dentry/block allocation/truncation
  - network setup
  - message buffers and queues
  - jukebox/SCSI/WORM operations
  - uid/gid/user commands
  - time/format/random helpers
  - process/locking/platform helpers
- External declarations:
  - `annstrs`
  - `bin`
  - `devmap`
  - `fsprotocol[]`.

Research notes:
- This header gives a concise cross-reference map of cwfs subsystem boundaries.
- It exposes both low-level device APIs (`wrenread`, `wormwrite`, `mcatread`, etc.) and high-level filesystem/admin APIs (`cfsdump`, `cmd_users`, `cmd_check`).
