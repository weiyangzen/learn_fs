# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/ip.h

Plan 9 IP address helper declarations.

Key contents:
- Defines IPv6-sized address length, IPv4 length, and IPv4-in-IPv6 offset constants.
- Declares IP parsing, mask, formatting, host/network byte-order, IPv4/IPv6 conversion, and predefined address globals.
- Defines `ipcmp` and `ipmove` as 16-byte memory operations.

Role in this group:
- Shared by drawterm networking and device code needing Plan 9-format IP addresses.

Notable risks:
- Uses `vlong` return values for parse helpers in the Plan 9 style; callers need implementation-specific error interpretation.
