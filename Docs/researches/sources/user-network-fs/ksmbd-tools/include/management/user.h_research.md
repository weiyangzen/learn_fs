<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/user.h -->
# sources/user-network-fs/ksmbd-tools/include/management/user.h

## Purpose

Declares the user-management model and login/logout handlers for mountd.

## Important APIs, Types, and Functions

Defines `struct ksmbd_user` with name, Base64 password hash, decoded hash, uid/gid, flags, state, locks, failed login count, and supplementary groups. Exposes lookup, refcount, add/remove/update, guest-account addition, iteration, and login/logout IPC handlers.

## Control Flow

Config loading populates the user table from pwddb and system passwd/group lookups. Login requests compare account state and password hash, map to uid/gid/groups, and logout updates session/account state.

## State and Persistence Behavior

State is in-memory user records plus persisted `ksmbdpwd.db` for non-guest accounts. Guest accounts and supplementary groups are derived at load time.

## Dependencies and Integration Points

Used by adduser, share policy, session/tree connect, RPC account lookup, and SPNEGO/login handlers.

## Risks and Edge Cases

Password hash storage and decoding must respect kernel hash-size limits. Refcounts and locks protect concurrent IPC handling. Deleting users while shares reference them is guarded by adduser but runtime reload ordering remains important.

## Test Signals

Tests should cover user name validation, guest account creation, hash decode, login success/failure flags, supplementary groups, failed counts, and reload replacement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/user.h -->
