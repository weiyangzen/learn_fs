# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/pass.c

Factotum protocol module that returns a stored username/password pair.

Key responsibilities:
- Finds a key with `user` and private `!password`.
- Returns quoted `user password` on read.
- Does not support writes or server-side authentication.
- Holds the selected key until close.

Dependencies:
- Uses factotum key lookup and quoting/attribute helpers.

Research notes:
- Comments explicitly discourage this as a general mechanism; it is just a password repository.
