# File Research: sources/os/plan9/9front/sys/src/cmd/venti/mkroot.c

Purpose: Creates and writes a Venti root block from command-line fields.

Key behavior:
- Accepts root name, type, data score, block size, and previous root score.
- Packs a `VtRoot`, writes it as `VtRootType`, syncs the server, and prints the resulting root score.
- Supports optional Venti host selection.

Dependencies:
- Uses Venti connection, score parsing, root packing, write, and sync APIs.

Notable details:
- This is a low-level root-construction utility independent of Vac-specific metadata.
