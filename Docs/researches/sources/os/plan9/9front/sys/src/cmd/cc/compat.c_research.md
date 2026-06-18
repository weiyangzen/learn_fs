# File Research: sources/os/plan9/9front/sys/src/cmd/cc/compat.c

Purpose: Includes shared compiler compatibility support.

Key points:
- Includes `cc.h`.
- Includes `"compat"` without an extension, relying on a repository/build-provided compatibility implementation file.

Dependencies and interactions:
- Uses declarations from `compat.h` via `cc.h`.
- Build system must provide the included `compat` file in the include path or current directory.

Research notes:
- This is a two-line include wrapper, not substantive implementation by itself.
