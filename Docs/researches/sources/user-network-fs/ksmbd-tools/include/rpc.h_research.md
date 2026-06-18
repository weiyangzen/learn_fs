<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc.h

## Purpose

Core declaration surface for ksmbd's lightweight DCE/RPC and NDR implementation used by IPC named-pipe services.

## Important APIs, Types, and Functions

Defines DCE/RPC flags, packet types, fragment flags, serialization constants, headers, NDR pointer/string wrappers, request structs for SRVSVC/WKSSVC/SAMR/LSARPC, syntax/context structures, `ksmbd_dcerpc`, `ksmbd_rpc_pipe`, NDR read/write helpers, pipe reset, RPC init/destroy, and open/write/read/ioctl/close entry points.

## Control Flow

Kernel RPC IPC calls open a pipe, write a request payload, parse DCE/RPC headers and service-specific arguments, later read a response payload, and close the pipe. Service implementations install entry callbacks for array serialization.

## State and Persistence Behavior

State is per-pipe: DCE payload cursor, request/response pointers, decoded headers, service request unions, pending entries, processed counters, and callback pointers. A global pipe table is maintained in rpc.c.

## Dependencies and Integration Points

Integrated with kernel `ksmbd_rpc_command` ABI, GLib arrays/tables, SRVSVC/WKSSVC/SAMR/LSARPC service files, and smbacl helpers.

## Risks and Edge Cases

The parser is intentionally partial and pointer/offset heavy. Fragmentation, endian flags, fixed payload limits, and service callback contracts are high-risk. Pipe and handle tables must be cleaned on close/destroy.

## Test Signals

Tests should exercise bind/alt-context negotiation, endian conversion, string conversion, fixed-buffer overflow, multi-part array responses, unknown opnums, and pipe lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc.h -->
