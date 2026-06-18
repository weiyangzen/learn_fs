# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscdefs.c

Duplicate configuration-scalar source matching `gscdef.c` in this tree.

Key contents:
- Includes `std.h`, `gscdefs.h`, and `gconfigd.h`.
- Defines the same build metadata, product strings, revision values, serial number, library path, documentation path, and init-file name as `gscdef.c`.
- Provides the same functions:
  - `gs_program_name()`
  - `gs_revision_number()`

Important implementation notes:
- The file body is identical to `gscdef.c` in the inspected Plan 9 Ghostscript snapshot, including the `$Id` line naming `gscdef.c`.
- This likely exists for build-system naming compatibility or historical source layout reasons.
- Treat as duplicate configuration definition code; linking both objects into one binary would normally create duplicate symbols unless the build chooses only one.
