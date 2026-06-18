# File Research: sources/os/linux/linux/fs/nfsd/current_stateid.h

Declares helpers for managing NFSv4 compound current stateid state.

Key behavior:
- Declares `clear_current_stateid()`.
- Declares setters for operations that produce/update current stateid:
  - open downgrade
  - open
  - lock
  - close
- Declares getters for operations that consume current stateid:
  - open downgrade
  - delegation return
  - free stateid
  - setattr
  - close
  - locku
  - read
  - write

Important interactions:
- Included by NFSD NFSv4 compound processing code.
- Encapsulates the RFC current-stateid mechanism across NFSv4 operations encoded in `union nfsd4_op_u`.
