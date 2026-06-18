# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/9pfreebsd/mount_9fs/crypt.c

Read fully: 415 lines, 18042 bytes. SHA-256 prefix: `c0d0f0af0350efa4`.

This file implements the DES block cipher routines needed by old Plan 9 password/key handling.

Important routines:
- `encrypt9()` destructively encrypts a buffer of at least 8 bytes using Plan 9’s overlapping 7-byte stepping convention.
- `decrypt()` reverses the same convention from the end of the buffer.
- `block_cipher()` performs 16 DES rounds using combined S/P-box lookup tables.
- `ip_low()`, `ip_high()`, and `fp()` implement initial/final permutations.
- `key_setup()` expands a 7-byte Plan 9 DES key into the 128-byte internal round-key table.

Integration: `mount_9fs.c` uses `passtokey()` and `encrypt9()` to derive a Plan 9-compatible DES key from a password.

Risk notes: this is legacy DES code. It also relies on assumptions about `long` width and signed byte behavior typical of the original environment.
