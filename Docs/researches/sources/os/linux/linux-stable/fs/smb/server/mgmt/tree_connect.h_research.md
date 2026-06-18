# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/tree_connect.h

Read status: complete.

## Purpose
Defines ksmbd tree-connect state and APIs.

## Main Contents
- Tree states: new, connected, disconnected.
- `struct ksmbd_tree_connect` with tree ID, flags, share config, user, access state, POSIX-extension flag, refcount, and state.
- `struct ksmbd_tree_conn_status` return wrapper.
- Flag test helper and APIs for connect, put, disconnect, lookup, and session logoff.

## Dependencies And Role
Used by SMB command handlers to bind session requests to shares.

## Risks
Lookup only returns `TREE_CONNECTED` refs; callers must put returned tree connections to avoid leaked share refs.
