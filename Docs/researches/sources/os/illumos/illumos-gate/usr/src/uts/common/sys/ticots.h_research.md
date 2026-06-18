# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticots.h

## Purpose
Defines compatibility error macros for the connection-oriented TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings for bad address/options, connection/reference errors, listener queue full, outstanding indications, no peer, bad peer state, and missing connection indications.

## Dependencies And Relationships
Used by legacy TICOTS consumers and compatibility documentation. Error values map to standard `errno` constants.

## Research Notes
Like `ticlts.h`, this is explicitly compatibility-only and not intended for new code.
