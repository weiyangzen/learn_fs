# File Research: sources/os/plan9/9front/sys/src/cmd/venti/read.c

Purpose: Reads one Venti block by score and writes its raw bytes to stdout.

Key behavior:
- Parses a score and optional host/type.
- If no type is specified, probes all Venti block types until a read succeeds and prints a reproducible command to stderr.
- Writes the retrieved block payload to stdout.

Dependencies:
- Uses Venti score parsing, connection, read, and formatting APIs.

Notable details:
- Allocates a full `VtMaxLumpSize` buffer to support any block type.
