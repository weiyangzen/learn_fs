# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/challenge.c

Interactive factotum challenge/response test utility.

Key points:
- Opens `/mnt/factotum/rpc`.
- Creates a challenge using `auth_challenge`.
- Prompts for user and response.
- Calls `auth_response` and prints client/server user IDs from returned `AuthInfo`.

Dependencies:
- Uses Plan 9 auth RPC/factotum APIs.

Notable behavior:
- Argument is passed as auth challenge parameters.
