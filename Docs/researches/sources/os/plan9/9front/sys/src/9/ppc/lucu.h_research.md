# File Research: sources/os/plan9/9front/sys/src/9/ppc/lucu.h

Assembly include for UCU/Saturn board support.

Key responsibilities:
- Provides assembler-visible memory mapping constants and board-specific low-level definitions for UCU builds.
- Supports alternate BAT/cache setup paths guarded by `ucuconf`.

Dependencies:
- Complements `ucu.h`/`msaturn` board configuration and low-level assembly.
