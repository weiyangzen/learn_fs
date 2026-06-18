# File Research: sources/os/plan9/9front/sys/src/cmd/5l/compat.c

This file is a tiny compatibility bridge for `5l`.

Key elements:
- Includes `l.h`.
- Includes the shared compiler compatibility implementation from `../cc/compat`.

Dependencies and integration:
- Provides the linker build with common compatibility functions/macros used across Plan 9 compiler tools.

Research notes:
- There is no local logic in this file; it exists to pull shared compatibility code into the `5l` build.
