# sources/sync-backup/borg/src/borg/fuse_impl.py

## Purpose
Selects the runtime FUSE binding used by Borg. It tries implementations listed in `BORG_FUSE_IMPL`, defaulting to `mfusepy,pyfuse3,llfuse`, and exposes shared module variables consumed by `fuse.py`, `hlfuse.py`, and diagnostics.

## Important APIs, Types, And Functions
Exports `BORG_FUSE_IMPL`, `hlfuse`, `llfuse`, `has_llfuse`, `has_pyfuse3`, `has_mfusepy`, `has_any_fuse`, and imports platform `ENOATTR`. There are no functions; import-time selection is the API.

## Control Flow
At import time, the comma-separated implementation preference list is normalized and processed in order. `pyfuse3` populates `llfuse` with the pyfuse3 module and marks `has_pyfuse3`; `llfuse` imports the low-level module; `mfusepy` populates `hlfuse`. The first successful import breaks the loop. `none` is accepted as a non-importing option, and unknown names raise `RuntimeError`.

## State And Persistence
All state is module-global and process-local. It does not persist anything, but import order matters because consumers branch on these booleans at import time.

## Dependencies And Integration Points
Integrated by low-level `fuse.py`, high-level `hlfuse.py`, and `helpers.misc.sysinfo`. It depends on optional third-party modules `mfusepy`, `pyfuse3`, and `llfuse`, plus Borg platform errno constants.

## Risks And Edge Cases
Because selection happens at import time, changing `BORG_FUSE_IMPL` later has no effect. A typo in the environment variable raises immediately. If all configured modules are unavailable, callers must tolerate `has_any_fuse=False`. The pyfuse3 branch deliberately assigns the module to `llfuse` for compatibility, so downstream code must always check the feature booleans.

## Test Signals
Mock or subprocess tests should cover preference ordering, `none`, unknown implementation names, absent optional imports, and `sysinfo` reporting.
