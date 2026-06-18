# File Research: sources/os/plan9/9front/sys/src/cmd/disk/cryptsetup.c

Small encrypted-disk setup/open helper for Plan 9’s `fs` crypt device.

Key behavior:
- `setupkey` derives an AES key from a password and salt using PBKDF2-HMAC-SHA1 with 9999 iterations, then initializes AES-CBC.
- `cformat` prompts for password confirmation, generates random master/slot data, encrypts the master key into slot 0, writes a 64KB randomized header, and stores a validation pad encrypted under the master key.
- `copen` reads the header, prompts/retries password, decrypts slot 0, validates the pad, and prints or installs a `/dev/fs/ctl` `crypt` command with the decrypted master key.
- Modes are `-f` format, `-o` print open command, and `-i` install/open through `/dev/fs/ctl`.

Notable dependencies:
- `libsec` AES/PBKDF2/HMAC/SHA1 and Plan 9 `readcons`.
- `/dev/fs/ctl` control protocol.

Research notes:
- Password buffers are wiped before free.
- Only slot 0 is actually used despite storage for 8 slots.
- This is a low-level destructive formatter when run with `-f`.
