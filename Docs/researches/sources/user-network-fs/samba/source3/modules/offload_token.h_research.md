# sources/user-network-fs/samba/source3/modules/offload_token.h

## Purpose
Public interface for Samba VFS offload token creation, lookup, and handle validation.

## APIs, Types, And Control Flow
Forward-declares `vfs_offload_ctx` and `req_resume_key_rsp`, defines token offsets for persistent id, volatile id, and fsctl, and declares context initialization, database store/fetch, token blob creation, and handle checking functions.

## State, Dependencies, Integration
The header has no state. It exposes fixed offsets that are shared with the implementation and VFS callers that may inspect token layout. Included by default, btrfs, and fruit VFS modules for ODX/copychunk support.

## Risks And Test Signals
The offset constants are ABI-like within Samba. Compile tests should ensure all callers agree on token size and offsets, and behavior tests should validate unsupported FSCTL handling.
