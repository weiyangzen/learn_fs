<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h -->
# sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h

## Purpose

Userspace copy of the ksmbd kernel IPC ABI. It defines generic-netlink family metadata, request/response payload structures, event IDs, flags, and RPC status codes shared between mountd and the kernel module.

## Important APIs, Types, and Functions

Important structures include startup/shutdown, login, share config, tree connect/disconnect, logout, RPC, and SPNEGO request/response messages. Important enums/macros cover `ksmbd_event`, tree connection statuses, user/share/global flags, RPC method flags, RPC error/status codes, and config option values.

## Control Flow

mountd fills startup requests from global configuration, receives typed kernel requests, dispatches them to user/share/session/tree/RPC/SPNEGO handlers, and replies with the matching event type. The header notes that response event values must equal request value plus one.

## State and Persistence Behavior

No direct state, but every structure represents serialized state across netlink. Many structures are packed or include flexible payload tails whose size fields control parsing.

## Dependencies and Integration Points

Used by ipc.c, management modules, addshare/adduser validation limits, RPC service code, and kernel-side ksmbd.

## Risks and Edge Cases

ABI drift is the central risk: field order, sizes, event numbering, and flags must stay synchronized with the kernel. Flexible payload offsets and fixed name/hash limits are easy boundary-error sites.

## Test Signals

Tests should pair a userspace build with kernel IPC tests for each event, verify response event numbering, and fuzz short/oversized payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h -->
