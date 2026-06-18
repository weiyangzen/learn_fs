# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timod.h

## Purpose
STREAMS Transport Interface module ioctl and synchronization definitions.

## Main Interfaces
- Defines `TIMOD` ioctl base and commands including `TI_GETINFO`, `TI_OPTMGMT`, `TI_BIND`, `TI_UNBIND`, `TI_GETMYNAME`, `TI_GETPEERNAME`, `TI_SYNC`, `TI_GETADDRS`, and `TI_CAPABILITY`.
- Defines `struct ti_sync_req` and `struct ti_sync_ack`.
- Defines sync request flags such as `TSRF_INFO_REQ`, `TSRF_IS_EXP_IN_RCVBUF`, and `TSRF_QLEN_REQ`.
- Defines `TSAF_EXP_QUEUED` acknowledgement flag.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/stream.h`. Used by the TLI/XTI STREAMS module to coordinate user-level transport library state with provider state.

## Research Notes
The header is internal STREAMS/TLI plumbing. Its structures are small but ABI-sensitive because ioctl payloads cross the user/kernel boundary.
