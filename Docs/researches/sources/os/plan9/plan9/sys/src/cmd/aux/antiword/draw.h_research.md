# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.h

This header defines small helper types for RISC OS Draw image handling.

Key behavior:
- Includes Draw type definitions.
- Defines JPEG stream header and JPEG stream structures compatible with Draw data.
- Provides a union that can view image payloads as sprite, JPEG, byte, or word pointers.

Important details:
- The structures mirror Draw object layout and are used by RISC OS image rendering paths.

Filesystem relevance:
- Indirect: data layout support for converted embedded document images.
