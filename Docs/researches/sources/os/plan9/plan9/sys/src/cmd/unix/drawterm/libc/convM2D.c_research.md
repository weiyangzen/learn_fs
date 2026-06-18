# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2D.c

This file validates and decodes 9P stat message bytes into `Dir`.

Key behavior:
- `statcheck` verifies total size and counted string layout.
- `convM2D` extracts fixed fields and optionally copies strings into caller-provided storage.

Important details:
- If no string storage is supplied, string fields point to a static empty string.
- Complements `convD2M`.
