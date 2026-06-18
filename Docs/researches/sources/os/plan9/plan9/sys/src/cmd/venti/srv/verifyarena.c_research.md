# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/verifyarena.c

Purpose: Verifies arena checksums and trailer consistency.

Key behavior:
- Can verify a single arena from stdin or selected arenas from an arena partition.
- Hashes arena data with the final score slot treated as zero, compares computed score to trailer score, and distinguishes sealed, unsealed, and mismatch cases.
- Validates header/trailer name and version consistency and prints arena metadata.

Dependencies:
- Uses raw file reads, arena partition parsing, arena head/tail unpacking, SHA1, and Venti formatting.

Notable details:
- Supports throttling via `-s ms`; `-v` is parsed but not used beyond incrementing a variable.
