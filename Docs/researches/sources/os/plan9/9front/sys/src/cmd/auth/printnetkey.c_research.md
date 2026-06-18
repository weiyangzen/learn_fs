# File Research: sources/os/plan9/9front/sys/src/cmd/auth/printnetkey.c

Network key display tool.

Key responsibilities:
- Looks up a user's DES network key in `NETKEYDB`.
- Prints it using the DES key formatter.
- Rejects overlong/non-NUL-terminated usernames.

Dependencies:
- Uses `finddeskey`, `deskeyfmt`, `NETKEYDB`, and shared `error`.
