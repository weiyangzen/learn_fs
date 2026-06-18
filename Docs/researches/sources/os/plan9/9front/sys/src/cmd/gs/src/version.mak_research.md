# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/version.mak

Ghostscript version makefile fragment.

Key points:
- Defines `GS_VERSION_MAJOR=8`, `GS_VERSION_MINOR=53`, and `GS_VERSION_MINOR0=53`.
- Defines `GS_REVISIONDATE=20051020`.
- Derives `GS_VERSION=853`, `GS_DOT_VERSION=8.53`, and `GS_REVISION=$(GS_VERSION)`.
- Used by build and installation makefiles for versioned paths, library names, archive names, and installer text.

Dependencies and interactions:
- Included by nearly every platform makefile in this group.
- `unix-dll.mak`, install fragments, and Windows packaging rules depend on these values.

Research relevance:
- Establishes this bundled Ghostscript source as version 8.53 with revision date 2005-10-20.
