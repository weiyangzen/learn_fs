<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h -->
# sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h

## Purpose

Declares tree-connection state for a connected user/share pair.

## Important APIs, Types, and Functions

Defines `struct ksmbd_tree_conn` with id, share pointer, and flags; flag helpers; and handlers for tree connect/disconnect requests.

## Control Flow

A tree-connect request resolves user/share policy, creates a connection object, attaches it to a session, and fills kernel response flags/status. Disconnect releases the share connection.

## State and Persistence Behavior

State is in-memory and linked from sessions. It references shares and carries connection flags such as guest, read-only, writable, admin, and update.

## Dependencies and Integration Points

Depends on management/share, management/user/session implementation, and kernel tree connection ABI.

## Risks and Edge Cases

Correct release on disconnect matters for share connection limits. Flag computation must match share/user policy.

## Test Signals

Tests should cover allowed/denied users, guest access, read/write flags, admin users, too-many-connections, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h -->
