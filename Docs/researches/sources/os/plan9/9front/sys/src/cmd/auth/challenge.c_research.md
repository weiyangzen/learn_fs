# File Research: sources/os/plan9/9front/sys/src/cmd/auth/challenge.c

Interactive factotum challenge-response tester.

Key responsibilities:
- Opens `/mnt/factotum/rpc`.
- Creates an auth challenge from the supplied parameter string.
- Prints the challenge, reads optional user and response from stdin, and submits the response.
- Prints authenticated client/server user ids from returned `AuthInfo`.

Dependencies:
- Uses Plan 9 auth challenge APIs and factotum rpc.

Research notes:
- The allocated `AuthRpc` is opened but not directly used after `auth_challenge()`, relying on auth library behavior.
