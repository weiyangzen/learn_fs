# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stmf_defines.h

## Role

Common STMF constants, status encoding, SCSI field helpers, sense/ASC/ASCQ constants, and forward declarations.

## Key Contents

Defines `BIT_0` through `BIT_31`. Defines `stmf_status_t` as `uint64_t` and status encoding constants for success, generic failure, target failure, LU failure, function-specific codes, retry bit, busy, not found, invalid argument, LUN taken, aborted, allocation failure, already, timeout, not supported, and bad state.

Provides byte-offset and aligned-structure-size macros plus big-endian SCSI integer readers for 16-, 21-, 32-, and 64-bit fields. Defines pointer/integer conversion macros, a synchronize-cache command not present elsewhere, and common packed SCSI sense/action codes used by STMF SCSI library status helpers.

## Design Notes

The status format reserves high bits for broad failure class and middle bits for framework-specific codes, allowing providers and core code to share compact status values.
