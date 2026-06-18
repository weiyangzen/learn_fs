# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzversion.c

Purpose: Implements the public libbzip2 version query.

Key points:
- `BZ2_bzlibVersion` returns `BZ_VERSION`.
- The file carries the same modified-upstream bzip2 notice and license text as the other split files.

Dependencies and interactions:
- Depends on `BZ_VERSION` from `bzlib_private.h`.
- Exposes a public API declared in `bzlib.h`.

Research notes:
- Minimal implementation; version identity is centralized in the private header.
