# File Research: sources/os/linux/linux-stable/fs/nfsd/current_stateid.h

Purpose: Declares helpers for NFSv4 compound current-stateid handling.

Key responsibilities:
- Declares clearing of current stateid in compound state.
- Declares setters for stateid-producing operations:
  - open downgrade,
  - open,
  - lock,
  - close.
- Declares getters for stateid-consuming operations:
  - open downgrade,
  - delegation return,
  - free stateid,
  - setattr,
  - close,
  - locku,
  - read,
  - write.

Integration:
- Used by NFSD NFSv4 compound operation processing.
- Depends on `state.h` and `xdr4.h`.

Risks and notes:
- Header only declares operation-specific plumbing; actual stateid semantics are implemented elsewhere.
