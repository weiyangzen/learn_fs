# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/tempnam.c

Compatibility implementation of `tempnam()` for V9/BSD/Plan 9 builds.

Key responsibilities:
- Checks candidate directory accessibility.
- Allocates a unique-ish path of the form `dir/pfx.pid.seq`.
- Loops while the path exists and sequence is below 256.

Important behavior:
- On Plan 9 it avoids write-access checking because access emulation has a race.

Notable risks:
- Name generation is inherently race-prone; caller must still create safely.
- If all 256 names exist, it returns the last allocated candidate without explicit failure.
