# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarena.c

`printarena` inspects one arena image. It reads and prints the arena header, initializes an `Arena`, then walks clumps from a requested offset or the start until free space or an invalid clump is reached.

For each clump it validates clump magic, loads data, recomputes score unless the clump is marked corrupt, validates the Venti type, and prints offset, score, type, and uncompressed size. It reports the final end offset.

The tool is read-only and useful for verifying a standalone arena dump or extracting clump listings without loading a full Venti configuration.
