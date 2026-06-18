# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys2.c

Converts old key database records to the newer encrypted key database format.

Key points:
- Reads old fixed-size records, decrypts each with the old auth key, copies into new record layout, and clears the secret field.
- Adds random header bytes and encrypts the new database with DES-CBC under a new password.
- Verbose mode prints usernames.

Dependencies:
- Uses `OKEYDBLEN`, `KEYDBLEN`, `KEYDBOFF`, and `SECRETLEN` from `authsrv.h`.

Notable behavior:
- Warns but still processes only full old-format records when file length is odd.
