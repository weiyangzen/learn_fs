# File Research: sources/os/plan9/9front/sys/src/cmd/auth/keyfs.c

9P key database file server for Plan 9 auth key files.

Key responsibilities:
- Mounts a virtual filesystem, default `/mnt/keys`, backed by encrypted `/adm/keys`-style database records.
- Supports DES and AES key database formats; AES format stores DES key, status, warnings, expiration, secret, and AES key per user.
- Decrypts/encrypts the backing key database with NVRAM key or entered password.
- Exposes users as directories with files: `key`, `aeskey`, `pakhash`, `secret`, `log`, `status`, `expire`, and `warnings`.
- Enforces disabled, expired, and purgatory states on key reads.
- Tracks bad login counts through `log`; repeated bad attempts trigger temporary purgatory.
- Supports user create, remove, rename, status updates, expiration updates, secret/key writes, and warning reset.
- Reloads the key database when the backing file mtime changes.
- Optionally runs a daily warning command.
- Supports read-only mounts and alternate mount/keyfile paths.

Dependencies:
- Uses 9P fcall encoding/decoding directly, auth command helpers, DES/AES CBC, NVRAM keys, PAK hash generation, and Plan 9 mount over a pipe.

Notable risks:
- The server rewrites the whole encrypted key file on most mutations.
- Usernames are fixed-length in the on-disk record and validated for UTF/control/slash/space issues.
- The virtual files are mode `0666`, relying on mount/auth service context and data checks rather than per-file Plan 9 ownership.
