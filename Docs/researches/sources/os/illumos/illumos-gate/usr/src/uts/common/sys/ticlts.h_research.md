# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticlts.h

## Purpose
Defines compatibility error macros for the connectionless TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings:
  - `TCL_BADADDR`
  - `TCL_BADOPT`
  - `TCL_NOPEER`
  - `TCL_PEERBADSTATE`

## Dependencies And Relationships
Used by old TICLTS consumers and documentation compatibility. Error values map to standard `errno` constants.

## Research Notes
The file explicitly says these old error codes are exposed only for compatibility and should not be used in new programs.
