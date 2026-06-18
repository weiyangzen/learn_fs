<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_samr.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_samr.h

## Purpose

Declares SAMR service support for account/domain management queries over DCE/RPC.

## Important APIs, Types, and Functions

Defines `struct connect_handle` with a 20-byte handle, refcount, and associated user; declares SAMR read/write handlers and init/destroy.

## Control Flow

rpc.c dispatches SAMR write/read phases. The implementation tracks connect/domain/user handles, domain entries, user lookups, user-info responses, group membership, and security descriptors.

## State and Persistence Behavior

State includes a SAMR connect-handle table, refcounts, optional user pointer, domain entries, and cached uppercase domain name.

## Dependencies and Integration Points

Depends on smbacl, user management, generic RPC helpers, and GLib.

## Risks and Edge Cases

Handle refcounts must match open/close call sequences. User pointers must remain valid across reloads or be released correctly by implementation.

## Test Signals

Tests should cover connect, enum/lookup/open domain, lookup/open user, query user info, query security, group membership, alias membership, close, and bad handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_samr.h -->
