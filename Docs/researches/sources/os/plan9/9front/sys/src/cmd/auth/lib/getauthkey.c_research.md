# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getauthkey.c

Loads the machine auth key from NVRAM or prompts for it.

Key responsibilities:
- Clears the target `Authkey`.
- Calls `readnvram`.
- On failure, prompts for the machine key using `getpass`.
- On success, copies DES and AES machine keys from `Nvrsafe`.
- Clears the temporary NVRAM structure.

Dependencies:
- Uses `Nvrsafe`, `readnvram`, `getpass`, and authsrv key constants.
