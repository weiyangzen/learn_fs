# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getauthkey.c

Reads the machine authentication key from nvram into an 8-byte DES key buffer. If nvram cannot be read, it prompts the operator to enter the machine key using `getpass`.

`getkey` zeroes the `Nvrsafe` struct after copying `machkey`; `getauthkey` always returns success after prompting fallback.
