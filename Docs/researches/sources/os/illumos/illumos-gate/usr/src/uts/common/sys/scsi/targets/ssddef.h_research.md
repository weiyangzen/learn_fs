# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ssddef.h

## Purpose
Backward-compatibility wrapper for old `ssd` semantics.

## Main Interfaces
- Forces `__fibre` to be defined if absent.
- Includes the real disk target header `sun/sys/scsi/targets/sddef.h`.

## Dependencies And Relationships
Compatibility layer for consumers expecting `ssddef.h`; actual definitions live in `sddef.h`.

## Research Notes
The file says `ssddef.h` is expected to become obsolete.

## Notable Risks
- The include path uses `sun/sys/...`, so build environments must preserve legacy include aliases.
- Defining `__fibre` changes conditional semantics in old consumers.
