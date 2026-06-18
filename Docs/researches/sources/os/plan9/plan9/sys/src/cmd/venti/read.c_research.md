# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/read.c

Purpose: read a single Venti block and write raw bytes to stdout.

Behavior:
- Parses a score and optional type/host.
- If type is omitted, probes all Venti types until a read succeeds and prints the discovered invocation to stderr.
- Reads up to `VtMaxLumpSize`, hangs up, and writes the block data to stdout.

Integration points:
- Simple diagnostic/client utility around `vtread`.

Risks:
- Type probing can find the first readable interpretation, which may not be the caller’s intended semantic type.
