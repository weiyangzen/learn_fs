# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ticotsord.h

## Purpose
Defines compatibility error macros for the orderly-release connection-oriented TPI loopback transport provider.

## Main Interfaces
- Includes `sys/tl.h`.
- Compatibility error mappings parallel TICOTS: address/options, connection/reference errors, full listener queue, outstanding indications, missing peer, bad peer state, and missing connection indications.

## Dependencies And Relationships
Used by old TICOTSORD consumers and compatibility documentation.

## Research Notes
The macros are retained only for old manual-page/API compatibility and should not be used in new programs.
