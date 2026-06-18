# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/changeuser.c

Creates or updates Plan 9 and SecureNet user credentials.

Key points:
- Options select Plan 9 (`-p`) and/or SecureNet (`-n`); default is Plan 9.
- Prompts before replacing existing keys.
- For Plan 9, collects password, updates key and optional secret, and updates account bio.
- For SecureNet, generates random DES key, writes it, prints key and checksum.
- `install` creates user directories, writes key files, and preserves/updates expiration.

Dependencies:
- Uses auth command library functions, key database paths, and `authsrv.h`.

Notable behavior:
- Validates username by `ANAMELEN`.
