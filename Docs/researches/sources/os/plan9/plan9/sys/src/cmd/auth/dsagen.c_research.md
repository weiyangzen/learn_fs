# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsagen.c

Generates a DSA private key for factotum.

Key points:
- Calls `dsagen(nil)`.
- Prints `key proto=dsa` with optional tag attributes and all public/private DSA fields.

Dependencies:
- Uses `libsec` and multiprecision formatting.

Notable behavior:
- Supports `-t 'attr=value ...'`.
