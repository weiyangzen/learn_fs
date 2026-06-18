# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFlags.hh

## Purpose
Defines SFS feature bits and stat-mode/device markers that plugins use to advertise capabilities and special file states.

## Important APIs, Types, And Functions
- Feature bits in namespace `XrdSfs`: `hasAUTZ`, `hasCHKP`, `hasGPF`, `hasGPFA`, `hasPGRW`, `hasPOSC`, `hasPRP2`, `hasPRXY`, `hasSXIO`, `hasNOSF`, `hasCACH`, `hasNAIO`, and `hasFICL`.
- `XRDSFS_POSCPEND` maps close-pending POSC state to `S_ISUID` on Solaris and `S_ISVTX` elsewhere.
- `XRDSFS_OFFLINE`, `XRDSFS_HASBKUP`, and `XRDSFS_RDVMASK` encode special regular-file attributes in the high byte of `st_rdev`.

## Control Flow
There is no executable control flow. Filesystems set feature bits in `XrdSfsFileSystem::FeatureSet`, and callers inspect `Features()` to decide optional behavior. Stat consumers inspect `st_rdev` markers only when the remaining `XRDSFS_RDVMASK` bits are zero.

## State And Persistence
Feature constants are compile-time values. POSC and offline/backup markers may be persisted indirectly through filesystem mode/stat metadata when implementations choose to encode them.

## Dependencies And Integration Points
Included by `XrdSfsInterface.cc` and filesystem plugins. It ties optional SFS capabilities to server behavior, including page read/write, checkpointing, third-party transfers, sendfile disabling, and exchange-buffer I/O.

## Risks And Edge Cases
Feature-bit compatibility depends on stable numeric values. Device-bit encoding assumes enough width in `dev_t` and may interact poorly with real device values if mask checks are wrong. POSC mode-bit choice is platform-specific.

## Test Signals
Verify feature negotiation from `XrdSfsFileSystem::Features()`, offline/backup stat interpretation with masked and unmasked `st_rdev`, and POSC marker behavior on Solaris and non-Solaris builds.
