# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys.c

Re-encrypts a current-format Plan 9 key database file.

Key points:
- Gets original key from auth key or password with `-p`.
- In verbose mode `-v`, decrypts and prints usernames without rewriting.
- Otherwise prompts for a new password, decrypts with old DES-CBC wrapper, validates UTF-8-like names, randomizes header bytes, re-encrypts, and writes back.
- Uses `/dev/random` with `rand` fallback.

Dependencies:
- Uses `authsrv.h` key database record sizes and DES helpers.

Notable behavior:
- Truncates odd trailing bytes that do not fit full key records.
