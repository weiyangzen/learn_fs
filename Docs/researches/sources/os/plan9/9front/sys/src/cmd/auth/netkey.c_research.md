# File Research: sources/os/plan9/9front/sys/src/cmd/auth/netkey.c

Interactive Securenet response calculator.

Key responsibilities:
- Refuses to run when `service=cpu`.
- Hardens itself with `private`.
- Prompts for a password and derives a DES key.
- Repeatedly reads numeric challenges from stdin and prints `netcrypt` responses.

Dependencies:
- Uses auth command helpers, `passtodeskey`, `netcrypt`, and console prompting.
