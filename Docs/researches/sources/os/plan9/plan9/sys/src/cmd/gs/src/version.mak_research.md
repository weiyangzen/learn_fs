# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/version.mak

Ghostscript version make fragment.

Key points:
- Defines Ghostscript version 8.53.
- Sets `GS_VERSION_MAJOR=8`, `GS_VERSION_MINOR=53`, `GS_VERSION_MINOR0=53`.
- Sets revision date `GS_REVISIONDATE=20051020`.
- Derives `GS_VERSION=853`, `GS_DOT_VERSION=8.53`, and `GS_REVISION=$(GS_VERSION)`.

Dependencies and interactions:
- Included by many makefiles to set install directories, sonames, archive names, packaging names, and documentation text.

Research relevance:
- Anchors this source import to Ghostscript 8.53-era build and runtime paths.
