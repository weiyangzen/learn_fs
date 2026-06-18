# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/readnvram.c

Reads auth nvram and prints a factotum `key proto=p9sk1 ... !hex=...` control line for the stored machine key. It tolerates `readnvram` returning `-1` if auth fields are still populated.

Rejects all-zero machine keys. Output includes a placeholder `!password=______`.
