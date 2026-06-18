# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pushtls.c

This file configures Plan 9 TLS over an fd.

Key behavior:
- `pushtls` opens TLS control/data paths, configures hash/encryption algorithms, role, and secret material.
- `finished` computes TLS finished-label selection for client/server handshakes.

Important details:
- Uses Plan 9 `#a/tls`-style device control rather than a direct TLS library.
- Handles algorithm strings and secret byte formatting.
