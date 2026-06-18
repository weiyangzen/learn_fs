<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/session.h -->
# sources/user-network-fs/ksmbd-tools/include/management/session.h

## Purpose

Declares session-management state for users connected to ksmbd shares.

## Important APIs, Types, and Functions

Defines `struct ksmbd_session` with session id, user pointer, update lock, tree connection list, and ref counter. Exposes capacity checking, tree connect/disconnect handlers, and init/destroy.

## Control Flow

The implementation tracks sessions, enforces `global_conf.sessions_cap`, associates tree connections with users, and removes tree connections on disconnect or logout paths.

## State and Persistence Behavior

State is an in-memory session table with referenced users and child tree connections. It is not persisted across mountd restart.

## Dependencies and Integration Points

Integrated with tree_conn management and kernel tree connect/disconnect IPC events.

## Risks and Edge Cases

Reference counts and lock ordering must prevent stale user/tree pointers. Capacity handling affects denial of new sessions.

## Test Signals

Tests should connect multiple sessions, enforce max active sessions, disconnect tree connections, and verify cleanup on user logout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/session.h -->
