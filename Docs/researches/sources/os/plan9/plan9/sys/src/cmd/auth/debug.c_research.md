# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/debug.c

Authentication setup diagnostic tool.

Key points:
- Scans `/mnt/factotum/ctl` for `proto=p9sk1` keys.
- For each key, attempts to dial the auth server for the domain and reports name-service lookup details.
- Optionally prompts for passwords and tests ticket requests using the user key and CPU server owner key.
- Verifies decrypted ticket numbers and challenge echoes to detect key mismatches or rogue auth servers.

Dependencies:
- Uses auth server ticket protocol, factotum attribute parsing, `csgetvalue`, and Plan 9 auth helpers.

Notable behavior:
- Contains placeholders/comments for further p9sk1 exchange tests that are not implemented.
