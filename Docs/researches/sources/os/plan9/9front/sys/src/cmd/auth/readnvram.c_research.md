# File Research: sources/os/plan9/9front/sys/src/cmd/auth/readnvram.c

NVRAM key dumper in factotum control format.

Key responsibilities:
- Reads `Nvrsafe` from NVRAM.
- Prints `p9sk1` key line when DES machine key is present.
- Prints `dp9ik` key line when AES machine key is present.
- Uses hex-encoded private key fields and placeholder password.
- Fails if no keys are available.

Dependencies:
- Uses `readnvram`, authsrv key constants, and hex formatter.
