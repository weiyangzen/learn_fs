# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauthsrv/_asrdresp.c

This file reads variable-length auth-server responses.

Key behavior:
- `_asrdresp` reads the decimal byte-count prefix, validates it, then reads the requested response bytes.

Important details:
- Handles malformed size fields and oversize responses by setting error strings.
- Used by auth-server protocol helpers that need counted replies.
