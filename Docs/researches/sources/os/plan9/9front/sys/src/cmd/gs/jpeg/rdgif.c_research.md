# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdgif.c

Purpose: placeholder `cjpeg` GIF input module.

Key contents:
- Includes `cdjpeg.h`.
- Compiled only when `GIF_SUPPORTED` is enabled.
- Exports `jinit_read_gif()`.

Important behavior:
- Actual GIF image reading was removed from the IJG distribution for LZW patent concerns.
- If compiled and selected, `jinit_read_gif()` prints an unsupported message and exits with failure.
- Returns `NULL` only to satisfy compilers; normal control flow exits.

Dependencies:
- `cdjpeg.h`, stdio, application exit constants.
