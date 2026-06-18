# sources/user-network-fs/samba/source4/ntvfs/ipc/ipc_rap.c

## Purpose

`ipc_rap.c` implements the IPC named-pipe RAP transaction dispatcher for legacy LAN Manager style APIs. It decodes RAP transaction parameters, dispatches supported calls, marshals fixed data records and string heaps, and returns SMB trans2 response buffers.

## Important APIs, Types, and Functions

The public entry point is `ipc_rap_call()`. Internal types include `struct rap_call`, `struct rap_string_heap`, and `struct rap_heap_save`. Helper APIs include `new_rap_srv_call()`, `rap_srv_pull_word()`, `rap_srv_pull_dword()`, `rap_srv_pull_string()`, `rap_srv_pull_bufsize()`, `rap_srv_pull_expect_multiple()`, `rap_push_string()`, `_rap_netshareenum()`, `_rap_netserverenum2()`, and `api_Unsupported()`. Supported commands are `NetShareEnum` and `NetServerEnum2`.

## Control Flow

`ipc_rap_call()` creates a RAP call context from incoming trans params/data, pulls call number, parameter descriptor, and data descriptor, creates NDR push contexts, finds a command by numeric RAP ID, and runs its handler. Each handler validates descriptors and level, calls the semantic RAP server function, then loops through available results, saving data/heap offsets before each item and rolling back if the fixed data area collides with the descending string heap. The final response prepends RAP status and convert offset, appends handler parameters, writes fixed data, then writes heap strings in reverse order.

## State and Persistence Behavior

The file has no persistent state. Per-call state stores NDR pull/push cursors, descriptor strings, output status, receive buffer sizes, and string heap bookkeeping. Output is written into `trans->out`.

## Dependencies and Integration Points

It depends on generated RAP NDR types, raw SMB trans structures, libndr, tevent/loadparm context, and server functions implemented in `rap_server.c`. It is part of the IPC NTVFS backend path that handles RAP over SMB transactions.

## Risks and Edge Cases

Descriptor parsing is strict and advances descriptor pointers as it reads. String heap overflow handling relies on correct rollback of NDR data offsets and heap state. `RAPNDR_FLAGS` includes a trailing semicolon in the macro body, which works in assignments but is stylistically fragile. Unsupported commands return RAP status `NERR_notsupported` with success NTSTATUS. Buffer-size and convert-offset compatibility are legacy-sensitive.

## Test Signals

Tests should cover NetShareEnum levels 0 and 1, NetServerEnum2 levels 0 and 1, invalid descriptors, invalid levels, small output buffers causing partial enumeration, unsupported call numbers, string heap ordering, empty comments, and malformed incoming NDR.
