# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_challenge.c

This file implements challenge/response auth setup and completion.

Key behavior:
- `auth_challenge` opens `/mnt/factotum/rpc`, starts an auth RPC, sends formatted parameters, and requests a challenge.
- `auth_response` sends a response and retrieves `AuthInfo`.
- `auth_freechal` releases the challenge state and associated RPC.

Important details:
- Uses `AuthRpc` verbs such as `start`, `read`, and `write`.
- Challenge bytes and user strings are copied into a `Chalstate`.
- On failure it closes RPC state and records errors through `werrstr`.
