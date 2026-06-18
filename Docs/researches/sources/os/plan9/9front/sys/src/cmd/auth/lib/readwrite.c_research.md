# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/readwrite.c

File-level key/secret read-write helpers for mounted auth key databases.

Key responsibilities:
- Reads and writes small files by path.
- Finds DES keys, AES keys, PAK hashes, combined `Authkey` records, and account secrets.
- When AES key exists, reads or computes PAK hash with `authpak_hash`.
- Writes DES keys, AES keys, combined keys, and secrets.
- Suppresses writing AES key when it is all zeros.

Dependencies:
- Uses keyfs file layout: `key`, `aeskey`, `pakhash`, and `secret`.
- Uses libsec constant-time comparison and auth PAK hashing.

Notable risks:
- Helpers expect exact byte counts for key files.
