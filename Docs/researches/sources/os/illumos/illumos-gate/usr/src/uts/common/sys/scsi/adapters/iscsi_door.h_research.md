# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_door.h

## Role

iSCSI door-call interface header used for kernel-to-user name service lookup support and iSCSI service status signaling.

## Key Elements

- Defines door request signature, version, maximum data size, opcodes, and status codes.
- `iscsi_door_msg_hdr_t` is the common message header.
- `getipnodebyname_req_t` encodes a hostname lookup request with name buffer offset/length, address family, and flags.
- `getipnodebyname_cnf_t` encodes lookup response metadata: required size, address list, address type/length, canonical name, aliases, and error number.
- Defines request/confirm/indication/message unions for generic door message handling.
- Under `_KERNEL`, copies relevant `netdb.h` constants and `AI_*` flags, defines a kernel `hostent`, and declares door init/term/bind/unbind plus kernel wrappers for `getipnodebyname` and `freehostent`.
- In userland, maps `kfreehostent` and `kgetipnodebyname` to libc functions.
- Defines iSCSI initiator SMF service status values: enabled, disabled, transition.

## Dependencies and Coupling

Used by iSCSI initiator code that needs name resolution from kernel context via a userland door server.

## Research Notes

The message format uses offsets and lengths rather than embedded pointers, making it suitable for door IPC buffers shared across address spaces.
