# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gx.h

Provides common internal Ghostscript library includes and pervasive opaque graphics-state type declarations.

Key definitions:
- Includes core error, I/O, common type, memory, and debugging headers for internal graphics code.
- Forward-declares `gs_imager_state` and `gs_state`.

Research notes:
- The comment notes that these opaque types are defined here because they are used pervasively, even though a higher-level header might be architecturally cleaner.
