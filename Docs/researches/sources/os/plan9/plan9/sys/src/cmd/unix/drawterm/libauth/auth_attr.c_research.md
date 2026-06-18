# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_attr.c

This file exposes parsed attributes from an auth RPC conversation.

Key behavior:
- `auth_attr` returns `_parseattr(rpc->arg)`.

Important details:
- Attribute parsing is delegated entirely to `attr.c`.
